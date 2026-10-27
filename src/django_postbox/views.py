from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.paginator import Paginator
from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.utils.functional import cached_property
from django.utils.module_loading import import_string
from django.views import View
from django.views.generic import TemplateView

from django_postbox.settings import settings
from django_postbox.storages import get_storage

if TYPE_CHECKING:
    import uuid

    from django.http import HttpRequest

    from django_postbox.storages import Inbox, StoredMessage

TABS = ("html", "text", "headers", "raw", "attachments")

# Untrusted mail HTML may only load images, styles and fonts; links open a new tab
MAIL_HTML_HEAD = (
    '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; '
    "img-src * data:; style-src 'unsafe-inline' *; font-src * data:\">"
    '<base target="_blank">'
)


def load_permission(permission: type | str) -> type:
    """A POSTBOX_PERMISSIONS entry is a class or its dotted path"""
    return import_string(permission) if isinstance(permission, str) else permission


class PermissionMixin(UserPassesTestMixin):
    """Allow access only when every POSTBOX_PERMISSIONS class grants it"""

    request: HttpRequest

    def test_func(self) -> bool:
        return all(
            load_permission(permission)().has_permission(self.request)
            for permission in settings.POSTBOX_PERMISSIONS
        )


class MessageMixin(PermissionMixin):
    kwargs: dict[str, Any]

    def get_message(self) -> StoredMessage:
        message = get_storage().get(self.kwargs["pk"])
        if message is None or message.hash != self.kwargs["hash"]:
            raise Http404("Message not found")
        return message


class PollMixin(TemplateView):
    """
    The polling element sends ?state= with the poll_state it was rendered with.
    While nothing changed, answer 204 (htmx skips the swap) before building the page.
    """

    @cached_property
    def poll_state(self) -> str:
        raise NotImplementedError

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if request.GET.get("state") == self.poll_state:
            return HttpResponse(status=204)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        return super().get_context_data(
            storage_label=get_storage().label, poll_state=self.poll_state, **kwargs
        )


class OverviewView(PermissionMixin, PollMixin):
    template_name = "postbox/overview.html"
    paginate_by = 25

    @cached_property
    def inboxes(self) -> list[Inbox]:
        return get_storage().inboxes()

    @cached_property
    def poll_state(self) -> str:
        if not self.inboxes:
            return "empty"
        total = sum(inbox.count for inbox in self.inboxes)
        return f"{total}.{self.inboxes[0].last_received.timestamp()}"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        query = self.request.GET.get("q", "").strip()
        matching = [
            inbox for inbox in self.inboxes if query.lower() in inbox.address.lower()
        ]
        page = Paginator(matching, self.paginate_by).get_page(
            self.request.GET.get("page")
        )
        return super().get_context_data(
            has_inboxes=bool(self.inboxes), page_obj=page, query=query, **kwargs
        )


class InboxView(PermissionMixin, PollMixin):
    """An inbox with its newest message opened"""

    template_name = "postbox/inbox.html"

    @cached_property
    def poll_state(self) -> str:
        return get_storage().inbox_state(self.kwargs["hash"])

    def get_selected(self, messages: list[StoredMessage]) -> StoredMessage:
        return messages[0]

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        all_messages = get_storage().messages(self.kwargs["hash"])
        if not all_messages:
            raise Http404("Inbox is empty")
        query = self.request.GET.get("q", "").strip()
        # ponytail: subject and sender only; searching bodies means parsing every mail
        messages = [
            item
            for item in all_messages
            if query.lower() in f"{item.subject} {item.sender}".lower()
        ]
        message = self.get_selected(messages or all_messages)
        tabs = TABS if message.html else tuple(tab for tab in TABS if tab != "html")
        tab = self.request.GET.get("tab", tabs[0])
        if tab not in tabs:
            tab = tabs[0]
        return super().get_context_data(
            address=all_messages[0].recipient,
            total=len(all_messages),
            messages=messages,
            query=query,
            message=message,
            position=next(
                (
                    index
                    for index, item in enumerate(messages, 1)
                    if item.id == message.id
                ),
                None,
            ),
            mail_html=MAIL_HTML_HEAD + message.html,
            tab=tab,
            tabs=tabs,
            **kwargs,
        )


class MessageView(MessageMixin, InboxView):
    def get_selected(self, messages: list[StoredMessage]) -> StoredMessage:
        return self.get_message()


class MessageRawView(MessageMixin, View):
    def get(self, request: HttpRequest, **kwargs: Any) -> HttpResponse:
        message = self.get_message()
        return HttpResponse(
            message.raw,
            content_type="message/rfc822",
            headers={"Content-Disposition": f'attachment; filename="{message.id}.eml"'},
        )


class AttachmentView(MessageMixin, View):
    def get(self, request: HttpRequest, index: int, **kwargs: Any) -> HttpResponse:
        attachments = self.get_message().attachments
        if index >= len(attachments):
            raise Http404("Attachment not found")
        attachment = attachments[index]
        filename = attachment.filename.replace('"', "")
        response = HttpResponse(
            attachment.content, content_type=attachment.content_type
        )
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response


class DeleteMessageView(MessageMixin, View):
    def post(self, request: HttpRequest, hash: str, pk: uuid.UUID) -> HttpResponse:
        get_storage().delete(self.get_message().id)
        if get_storage().messages(hash):
            return redirect("postbox:inbox", hash=hash)
        return redirect("postbox:overview")


class ClearView(PermissionMixin, View):
    def post(self, request: HttpRequest, hash: str | None = None) -> HttpResponse:
        get_storage().clear(hash)
        return redirect("postbox:overview")
