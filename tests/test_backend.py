import pytest
from django.core import mail
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import EmailMessage

from django_postbox.backends import EmailBackend
from tests.conftest import LOCMEM_BACKEND, POSTBOX_BACKEND

requires_mailers = pytest.mark.skipif(
    not hasattr(mail, "mailers"), reason="MAILERS is Django 6.1+"
)


def test_captures_one_copy_per_recipient_and_forwards(storage, send, welcome):
    welcome.bcc = ["audit@example.com"]
    assert send(welcome) == 1

    assert sorted(m.recipient for m in storage.messages()) == [
        "alice@example.com",
        "audit@example.com",
        "bob@example.com",
    ]
    assert len(mail.outbox) == 1


def test_skip_domains_are_forwarded_not_captured(storage, send, settings):
    settings.POSTBOX_SKIP_DOMAINS = ["@Company.com"]
    send(
        EmailMessage(
            "internal", "x", "me@example.com", ["dev@company.com", "a@eu.company.com"]
        ),
        EmailMessage(
            "mixed", "x", "me@example.com", ["dev@company.com", "x@example.com"]
        ),
        EmailMessage("lookalike", "x", "me@example.com", ["x@notcompany.com"]),
    )
    assert sorted(m.recipient for m in storage.messages()) == [
        "x@example.com",
        "x@notcompany.com",
    ]
    assert len(mail.outbox) == 3


def test_capture_only_without_forward_backend(storage, settings):
    settings.POSTBOX_FORWARD_BACKEND = None
    with EmailBackend() as backend:
        sent = backend.send_messages(
            [EmailMessage("hi", "x", "me@example.com", ["a@example.com"])]
        )
    assert sent == 1
    assert len(storage.messages()) == 1
    assert mail.outbox == []


def test_forwarding_to_itself_is_refused(settings):
    settings.POSTBOX_FORWARD_BACKEND = POSTBOX_BACKEND
    with pytest.raises(ImproperlyConfigured):
        EmailBackend()


def test_storage_errors_raise_unless_fail_silently(settings, send):
    settings.POSTBOX_STORAGE = "django_postbox.storages.BaseStorage"
    message = EmailMessage("hi", "x", "me@example.com", ["a@example.com"])
    with pytest.raises(NotImplementedError):
        send(message)

    backend = EmailBackend()
    backend.fail_silently = True
    assert backend.send_messages([message]) == 1


@requires_mailers
def test_forward_to_mailers_alias(storage, settings):
    settings.MAILERS = {
        "default": {"BACKEND": POSTBOX_BACKEND, "OPTIONS": {"forward_to": "outbox"}},
        "outbox": {"BACKEND": LOCMEM_BACKEND},
    }
    sent = EmailMessage("hi", "x", "me@example.com", ["a@example.com"]).send()
    assert sent == 1
    assert len(storage.messages()) == 1
    assert len(mail.outbox) == 1


@requires_mailers
def test_forward_to_postbox_alias_is_refused(settings):
    settings.MAILERS = {
        "default": {"BACKEND": POSTBOX_BACKEND, "OPTIONS": {"forward_to": "default"}},
    }
    with pytest.raises(ImproperlyConfigured):
        mail.mailers.default  # noqa: B018
