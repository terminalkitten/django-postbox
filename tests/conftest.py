import pytest
from django.core.mail import EmailMultiAlternatives

from django_postbox.backends import EmailBackend
from django_postbox.storages import get_storage

POSTBOX_BACKEND = "django_postbox.backends.EmailBackend"
LOCMEM_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
STORAGES = ["DatabaseStorage", "MemoryStorage", "CacheStorage"]


@pytest.fixture(params=STORAGES)
def storage(request, settings, db):
    settings.POSTBOX_STORAGE = f"django_postbox.storages.{request.param}"
    storage = get_storage()
    storage.clear()
    yield storage
    storage.clear()


@pytest.fixture
def send(settings):
    """Send mail through the postbox backend, forwarding to locmem (mail.outbox)"""
    settings.POSTBOX_FORWARD_BACKEND = LOCMEM_BACKEND

    def send(*email_messages):
        return EmailBackend().send_messages(email_messages)

    return send


@pytest.fixture
def welcome():
    message = EmailMultiAlternatives(
        subject="Welcome",
        body="Hi Alice",
        from_email="noreply@example.com",
        to=["Alice <Alice@Example.com>"],
        cc=["bob@example.com"],
    )
    message.attach_alternative(
        "<h1>Hi Alice</h1><script>alert(1)</script>", "text/html"
    )
    message.attach("notes.bin", b"notes", "application/octet-stream")
    return message
