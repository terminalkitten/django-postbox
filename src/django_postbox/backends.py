from __future__ import annotations

from email.utils import parseaddr
from typing import TYPE_CHECKING, Any

from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured
from django.core.mail.backends.base import BaseEmailBackend
from django.utils.module_loading import import_string

from django_postbox.settings import settings
from django_postbox.storages import StoredMessage, get_storage

if TYPE_CHECKING:
    from collections.abc import Sequence

    from django.core.mail import EmailMessage


def is_skipped(address: str) -> bool:
    """True when the address is on a POSTBOX_SKIP_DOMAINS domain or subdomain"""
    domain = address.rpartition("@")[2].lower()
    return any(
        domain == skipped or domain.endswith(f".{skipped}")
        for skipped in (
            skip.lower().lstrip("@") for skip in settings.POSTBOX_SKIP_DOMAINS
        )
    )


def ensure_not_postbox(backend_path: str) -> None:
    if issubclass(import_string(backend_path), EmailBackend):
        raise ImproperlyConfigured("Postbox cannot forward mail to a postbox backend")


class EmailBackend(BaseEmailBackend):
    """
    Capture mail into the postbox storage, then pass every message on to the
    next backend: the `forward_to` MAILERS alias (Django 6.1+) or the
    POSTBOX_FORWARD_BACKEND dotted path. Mail to POSTBOX_SKIP_DOMAINS is not captured.
    """

    def __init__(
        self, *args: Any, forward_to: str | None = None, **kwargs: Any
    ) -> None:
        super().__init__(*args, **kwargs)
        # Django 6.1 deprecates fail_silently on the base class, so keep our own
        self.fail_silently = bool(args[0] if args else kwargs.get("fail_silently"))
        self.forward_backend = self.build_forward_backend(forward_to)

    def build_forward_backend(self, forward_to: str | None) -> BaseEmailBackend | None:
        if forward_to:
            from django.core.mail import mailers

            mailer_config = getattr(django_settings, "MAILERS", {}).get(forward_to, {})
            if backend_path := mailer_config.get("BACKEND"):
                ensure_not_postbox(backend_path)
            return mailers[forward_to]
        if backend_path := settings.POSTBOX_FORWARD_BACKEND:
            ensure_not_postbox(backend_path)
            options = {"fail_silently": True} if self.fail_silently else {}
            return import_string(backend_path)(**options)
        return None

    def open(self) -> bool | None:
        return self.forward_backend.open() if self.forward_backend else None

    def close(self) -> None:
        if self.forward_backend:
            self.forward_backend.close()

    def capture(self, email_message: EmailMessage) -> bool:
        recipients = dict.fromkeys(
            address.lower()
            for _, address in map(parseaddr, email_message.recipients())
            if address and not is_skipped(address)
        )
        if not recipients:
            return False
        raw = email_message.message().as_bytes()
        storage = get_storage()
        for recipient in recipients:
            storage.save(
                StoredMessage(
                    recipient=recipient,
                    sender=str(email_message.from_email),
                    subject=str(email_message.subject),
                    raw=raw,
                )
            )
        return True

    def send_messages(self, email_messages: Sequence[EmailMessage]) -> int:
        captured_count = 0
        for email_message in email_messages:
            try:
                captured_count += self.capture(email_message)
            except Exception:
                if not self.fail_silently:
                    raise
        if self.forward_backend:
            return self.forward_backend.send_messages(email_messages) or 0
        return captured_count
