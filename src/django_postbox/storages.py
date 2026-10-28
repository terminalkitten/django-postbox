from __future__ import annotations

import hashlib
import threading
import time
import uuid
from dataclasses import dataclass, field, replace
from email import message_from_bytes, policy
from functools import cached_property
from typing import TYPE_CHECKING

from django.core.cache import caches
from django.db.models import Count, Max, OuterRef, Subquery
from django.utils import timezone
from django.utils.module_loading import import_string

from django_postbox.settings import settings

if TYPE_CHECKING:
    from datetime import datetime
    from email.message import EmailMessage

    from django_postbox.models import Message

__all__ = [
    "Attachment",
    "BaseStorage",
    "CacheStorage",
    "DatabaseStorage",
    "Inbox",
    "MemoryStorage",
    "StoredMessage",
    "get_storage",
    "hash_address",
]


def hash_address(address: str) -> str:
    """Short, stable id of an inbox address, used in URLs"""
    return hashlib.sha256(address.strip().lower().encode()).hexdigest()[:16]


@dataclass(frozen=True)
class Attachment:
    filename: str
    content_type: str
    content: bytes


@dataclass(frozen=True)
class Inbox:
    address: str
    hash: str
    count: int
    last_received: datetime
    last_subject: str = ""


@dataclass
class StoredMessage:
    """A captured mail as one recipient received it"""

    recipient: str
    sender: str
    subject: str
    raw: bytes
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime = field(default_factory=timezone.now)

    @cached_property
    def hash(self) -> str:
        return hash_address(self.recipient)

    @cached_property
    def email(self) -> EmailMessage:
        return message_from_bytes(self.raw, policy=policy.default)

    def get_body(self, subtype: str) -> str:
        body = self.email.get_body(preferencelist=(subtype,))
        return body.get_content() if body else ""

    @cached_property
    def html(self) -> str:
        return self.get_body("html")

    @cached_property
    def text(self) -> str:
        return self.get_body("plain")

    @property
    def raw_text(self) -> str:
        return self.raw.decode(errors="replace")

    @cached_property
    def headers(self) -> list[tuple[str, str]]:
        return [(name, str(value)) for name, value in self.email.items()]

    @cached_property
    def attachments(self) -> list[Attachment]:
        return [
            Attachment(
                filename=part.get_filename() or f"attachment-{index}",
                content_type=part.get_content_type(),
                content=payload if isinstance(payload, bytes) else b"",
            )
            for index, part in enumerate(self.email.iter_attachments())
            if (payload := part.get_payload(decode=True)) is not None
        ]


class BaseStorage:
    """Where captured mail lives; subclasses implement save, list, get, delete"""

    label = "Custom"

    def save(self, message: StoredMessage) -> None:
        raise NotImplementedError

    def messages(self, hash: str | None = None) -> list[StoredMessage]:
        """Messages newest first, optionally for one inbox"""
        raise NotImplementedError

    def get(self, pk: uuid.UUID) -> StoredMessage | None:
        raise NotImplementedError

    def delete(self, pk: uuid.UUID) -> None:
        raise NotImplementedError

    def clear(self, hash: str | None = None) -> None:
        for message in self.messages(hash):
            self.delete(message.id)

    def inbox_state(self, hash: str) -> str:
        """Changes whenever mail arrives in or leaves the inbox; polled every 5s"""
        messages = self.messages(hash)
        return f"{len(messages)}.{messages[0].id}" if messages else "empty"

    def inboxes(self) -> list[Inbox]:
        """Every address that received mail, most recent first"""
        inboxes: dict[str, Inbox] = {}
        for message in self.messages():  # newest first, so the first hit is the latest
            if existing := inboxes.get(message.hash):
                inboxes[existing.hash] = replace(existing, count=existing.count + 1)
            else:
                inboxes[message.hash] = Inbox(
                    message.recipient,
                    message.hash,
                    1,
                    message.created_at,
                    message.subject,
                )
        return list(inboxes.values())


def filter_newest_first(
    messages: list[StoredMessage], hash: str | None
) -> list[StoredMessage]:
    return sorted(
        (message for message in messages if hash is None or message.hash == hash),
        key=lambda message: message.created_at,
        reverse=True,
    )


class DatabaseStorage(BaseStorage):
    """Stores mail in the Message model; shared by every process"""

    label = "Database"

    @staticmethod
    def to_stored(instance: Message) -> StoredMessage:
        return StoredMessage(
            id=instance.id,
            recipient=instance.recipient,
            sender=instance.sender,
            subject=instance.subject,
            raw=bytes(instance.raw),
            created_at=instance.created_at,
        )

    @property
    def model(self) -> type[Message]:
        from django_postbox.models import Message

        return Message

    def save(self, message: StoredMessage) -> None:
        self.model.objects.create(
            id=message.id,
            recipient=message.recipient,
            hash=message.hash,
            sender=message.sender,
            subject=message.subject,
            raw=message.raw,
            created_at=message.created_at,
        )

    def messages(self, hash: str | None = None) -> list[StoredMessage]:
        # ponytail: loads raw bytes for list views too; ~30ms for a 500 mail inbox,
        # mostly template rendering. Defer raw and paginate the list when inboxes get big
        queryset = self.model.objects.all()
        if hash is not None:
            queryset = queryset.filter(hash=hash)
        return [self.to_stored(instance) for instance in queryset]

    def get(self, pk: uuid.UUID) -> StoredMessage | None:
        instance = self.model.objects.filter(pk=pk).first()
        return self.to_stored(instance) if instance else None

    def delete(self, pk: uuid.UUID) -> None:
        self.model.objects.filter(pk=pk).delete()

    def clear(self, hash: str | None = None) -> None:
        queryset = self.model.objects.all()
        if hash is not None:
            queryset = queryset.filter(hash=hash)
        queryset.delete()

    def inbox_state(self, hash: str) -> str:
        # Two small queries instead of loading and parsing every message
        queryset = self.model.objects.filter(hash=hash)
        newest_id = queryset.values_list("id", flat=True).first()
        return f"{queryset.count()}.{newest_id}" if newest_id else "empty"

    def inboxes(self) -> list[Inbox]:
        newest = self.model.objects.filter(hash=OuterRef("hash")).order_by(
            "-created_at"
        )
        rows = (
            self.model.objects.values("hash")
            .annotate(
                address=Max("recipient"),
                count=Count("id"),
                last_received=Max("created_at"),
                last_subject=Subquery(newest.values("subject")[:1]),
            )
            .order_by("-last_received")
        )
        return [
            Inbox(
                row["address"],
                row["hash"],
                row["count"],
                row["last_received"],
                row["last_subject"],
            )
            for row in rows
        ]


class MemoryStorage(BaseStorage):
    """Keeps mail in this process only; lost on restart, not shared between workers"""

    label = "Memory"

    stored_messages: dict[uuid.UUID, StoredMessage] = {}  # noqa: RUF012 (shared on purpose)
    lock = threading.Lock()

    def save(self, message: StoredMessage) -> None:
        with self.lock:
            self.stored_messages[message.id] = message

    def messages(self, hash: str | None = None) -> list[StoredMessage]:
        with self.lock:
            messages = list(self.stored_messages.values())
        return filter_newest_first(messages, hash)

    def get(self, pk: uuid.UUID) -> StoredMessage | None:
        return self.stored_messages.get(pk)

    def delete(self, pk: uuid.UUID) -> None:
        with self.lock:
            self.stored_messages.pop(pk, None)


class CacheStorage(BaseStorage):
    """Keeps mail in a Django cache (POSTBOX_CACHE), shared by every process using it"""

    label = "Cache"

    INDEX_KEY = "postbox:index"
    LOCK_KEY = "postbox:lock"
    LOCK_TIMEOUT = 5

    @property
    def cache(self):  # noqa: ANN201 (BaseCache)
        return caches[settings.POSTBOX_CACHE]

    @staticmethod
    def message_key(pk: uuid.UUID) -> str:
        return f"postbox:message:{pk}"

    def update_index(
        self, add: uuid.UUID | None = None, remove: uuid.UUID | None = None
    ) -> None:
        # ponytail: cache.add spin lock, gives up after LOCK_TIMEOUT and writes anyway;
        # a lost index entry only hides a mail. Use DatabaseStorage for heavy concurrency.
        deadline = time.monotonic() + self.LOCK_TIMEOUT
        while not self.cache.add(self.LOCK_KEY, 1, self.LOCK_TIMEOUT):
            if time.monotonic() > deadline:
                break
            time.sleep(0.01)
        try:
            message_ids: list[uuid.UUID] = self.cache.get(self.INDEX_KEY, [])
            if add is not None:
                message_ids.append(add)
            if remove is not None and remove in message_ids:
                message_ids.remove(remove)
            self.cache.set(self.INDEX_KEY, message_ids, None)
        finally:
            self.cache.delete(self.LOCK_KEY)

    def save(self, message: StoredMessage) -> None:
        self.cache.set(self.message_key(message.id), message, None)
        self.update_index(add=message.id)

    def messages(self, hash: str | None = None) -> list[StoredMessage]:
        message_ids = self.cache.get(self.INDEX_KEY, [])
        messages_by_key = self.cache.get_many(
            [self.message_key(pk) for pk in message_ids]
        )
        return filter_newest_first(list(messages_by_key.values()), hash)

    def get(self, pk: uuid.UUID) -> StoredMessage | None:
        return self.cache.get(self.message_key(pk))

    def delete(self, pk: uuid.UUID) -> None:
        self.cache.delete(self.message_key(pk))
        self.update_index(remove=pk)


def get_storage() -> BaseStorage:
    return import_string(settings.POSTBOX_STORAGE)()
