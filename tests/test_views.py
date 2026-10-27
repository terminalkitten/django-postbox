import platform
import uuid

import django
import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from django_postbox.storages import hash_address

ALICE = hash_address("alice@example.com")


@pytest.fixture
def staff_client(client, db):
    client.force_login(User.objects.create(username="staff", is_staff=True))
    return client


@pytest.fixture
def message(storage, send, welcome):
    send(welcome)
    return storage.messages(ALICE)[0]


def message_url(name, message, *args):
    return reverse(f"postbox:{name}", args=[message.hash, message.id, *args])


def test_anonymous_is_sent_to_login(client, db):
    response = client.get(reverse("postbox:overview"))
    assert response.status_code == 302
    assert "login" in response.url


def test_non_staff_is_forbidden(client, db):
    client.force_login(User.objects.create(username="user"))
    assert client.get(reverse("postbox:overview")).status_code == 403


def test_permissions_from_settings_as_classes_or_strings(client, db, settings):
    settings.POSTBOX_PERMISSIONS = ["django_postbox.permissions.AllowAny"]
    assert client.get(reverse("postbox:overview")).status_code == 200
    from django_postbox.permissions import DebugOnly

    settings.DEBUG = False
    settings.POSTBOX_PERMISSIONS = [DebugOnly]
    assert client.get(reverse("postbox:overview")).status_code == 302


def test_overview_lists_inboxes(staff_client, message):
    response = staff_client.get(reverse("postbox:overview"))
    assert response.status_code == 200
    assert b"alice@example.com" in response.content
    assert b"bob@example.com" in response.content
    assert b"htmx.min.js" in response.content


@pytest.mark.parametrize("theme", ["mail2003", "mail2000", "mail2010", "modern"])
def test_bundled_themes_exist(staff_client, storage, settings, theme):
    from django.contrib.staticfiles import finders

    settings.POSTBOX_THEME = theme
    assert (
        f"themes/{theme}.css".encode()
        in staff_client.get(reverse("postbox:overview")).content
    )
    assert finders.find(f"postbox/themes/{theme}.css")


def test_mail2003_is_the_default_theme(settings):
    from django_postbox.settings import PostboxSettings

    del settings.POSTBOX_THEME
    assert PostboxSettings().POSTBOX_THEME == "mail2003"


def test_overview_without_htmx_or_theme(staff_client, storage, settings):
    settings.POSTBOX_LOAD_HTMX = False
    settings.POSTBOX_THEME = None
    response = staff_client.get(reverse("postbox:overview"))
    assert b"No mail captured yet" in response.content
    assert b"htmx.min.js" not in response.content
    assert b"themes/" not in response.content
    assert b"postbox.css" in response.content


def test_ago_filter():
    from datetime import timedelta

    from django.utils import timezone

    from django_postbox.templatetags.postbox import ago

    assert ago(timezone.now()) == "just now"
    assert ago(timezone.now() - timedelta(minutes=5)) == "5\xa0minutes ago"


def test_inbox_opens_newest_message(staff_client, storage, send, welcome, message):
    welcome.subject = "Newest"
    send(welcome)
    response = staff_client.get(reverse("postbox:inbox", args=[ALICE]))
    assert response.status_code == 200
    assert response.context["message"].subject == "Newest"
    assert reverse("postbox:overview").encode() in response.content


def test_status_bar(staff_client, storage, send, welcome, message):
    send(welcome)
    response = staff_client.get(message_url("message", message), {"tab": "raw"})
    content = response.content.decode()
    assert 'id="status"' in content
    assert "Message 2 of 2" in content
    assert "Raw view" in content
    assert response.context["storage_label"] in {"Database", "Memory", "Cache"}

    response = staff_client.get(reverse("postbox:overview"), {"q": "alice"})
    assert "1 inbox matching" in response.content.decode()


def test_inbox_search(staff_client, storage, send, welcome, message):
    welcome.subject = "Invoice 42"
    send(welcome)
    url = reverse("postbox:inbox", args=[ALICE])

    response = staff_client.get(url, {"q": "invoice"})
    assert [item.subject for item in response.context["messages"]] == ["Invoice 42"]
    assert "1 of 2 matching" in response.content.decode()
    assert "?q=invoice" in response.content.decode()

    response = staff_client.get(url, {"q": "noreply@"})
    assert len(response.context["messages"]) == 2

    response = staff_client.get(url, {"q": "nothing"})
    assert "No mail matches" in response.content.decode()
    assert response.context["message"].subject == "Invoice 42"

    response = staff_client.get(message_url("message", message), {"q": "invoice"})
    assert response.context["position"] is None


def test_inbox_poll_is_204_while_unchanged(
    staff_client, storage, send, welcome, message
):
    url = reverse("postbox:inbox", args=[ALICE])
    state = staff_client.get(url).context["poll_state"]
    assert staff_client.get(url, {"state": state}).status_code == 204

    send(welcome)
    assert staff_client.get(url, {"state": state}).status_code == 200


def test_overview_poll_is_204_while_unchanged(staff_client, storage, message):
    url = reverse("postbox:overview")
    state = staff_client.get(url).context["poll_state"]
    assert staff_client.get(url, {"state": state, "q": "x"}).status_code == 204


def test_overview_search(staff_client, message):
    response = staff_client.get(reverse("postbox:overview"), {"q": "BOB"})
    assert [inbox.address for inbox in response.context["page_obj"]] == [
        "bob@example.com"
    ]

    response = staff_client.get(reverse("postbox:overview"), {"q": "nobody"})
    assert "No inbox matches" in response.content.decode()


def test_overview_pagination(staff_client, storage, send, welcome):
    welcome.cc = []
    welcome.to = [f"user{number}@example.com" for number in range(30)]
    send(welcome)
    response = staff_client.get(reverse("postbox:overview"), {"page": 2})
    assert len(response.context["page_obj"]) == 15
    assert b"Page 2 of 2" in response.content


def test_empty_inbox_is_404(staff_client, storage):
    assert (
        staff_client.get(reverse("postbox:inbox", args=["0" * 16])).status_code == 404
    )


@pytest.mark.parametrize(
    ("tab", "expected"),
    [
        ("html", b"<iframe"),
        ("text", b"Hi Alice"),
        ("headers", b"Content-Type"),
        ("raw", b"MIME-Version"),
        ("attachments", b"notes.bin"),
        ("bogus", b"<iframe"),
    ],
)
def test_message_tabs(staff_client, message, tab, expected):
    response = staff_client.get(message_url("message", message), {"tab": tab})
    assert response.status_code == 200
    assert expected in response.content


def test_message_without_html_has_no_html_tab(staff_client, storage, send, welcome):
    welcome.alternatives = []
    send(welcome)
    message = storage.messages(ALICE)[0]
    response = staff_client.get(message_url("message", message), {"tab": "html"})
    assert b"<iframe" not in response.content
    assert response.context["tab"] == "text"
    assert "html" not in response.context["tabs"]


def test_message_from_other_inbox_is_404(staff_client, message):
    url = reverse("postbox:message", args=[hash_address("bob@example.com"), message.id])
    assert staff_client.get(url).status_code == 404
    url = reverse("postbox:message", args=[ALICE, uuid.uuid4()])
    assert staff_client.get(url).status_code == 404


def test_html_body_is_sandboxed(staff_client, message):
    response = staff_client.get(message_url("message", message))
    content = response.content.decode()
    assert 'sandbox="allow-popups allow-popups-to-escape-sandbox"' in content
    # Escaped into the srcdoc attribute, never part of our own page
    assert "<script>alert(1)</script>" not in content
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in content
    assert response.context["mail_html"].startswith(
        '<meta http-equiv="Content-Security-Policy"'
    )


def test_raw_download(staff_client, message):
    response = staff_client.get(message_url("message_raw", message))
    assert response["Content-Type"] == "message/rfc822"
    assert f"{message.id}.eml" in response["Content-Disposition"]


def test_attachment_download(staff_client, message):
    response = staff_client.get(message_url("attachment", message, 0))
    assert response.content == b"notes"
    assert 'filename="notes.bin"' in response["Content-Disposition"]
    assert staff_client.get(message_url("attachment", message, 1)).status_code == 404


def test_delete(staff_client, storage, send, welcome, message):
    send(welcome)
    response = staff_client.post(message_url("delete", message))
    assert response.url == reverse("postbox:inbox", args=[ALICE])

    last = storage.messages(ALICE)[0]
    response = staff_client.post(message_url("delete", last))
    assert response.url == reverse("postbox:overview")
    assert storage.messages(ALICE) == []


def test_clear_inbox_and_all(staff_client, storage, message):
    staff_client.post(reverse("postbox:clear", args=[ALICE]))
    assert [m.recipient for m in storage.messages()] == ["bob@example.com"]
    staff_client.post(reverse("postbox:clear_all"))
    assert storage.messages() == []


def test_settings_page_shows_versions_and_themes(staff_client, storage):
    response = staff_client.get(reverse("postbox:settings"), {"next": "/dev/inbox/"})
    content = response.content.decode()
    assert response.status_code == 200
    assert "About Postbox" in content
    assert "Version" in content
    # No server details: they help attackers more than developers
    assert "django_version" not in response.context
    assert django.get_version() not in content
    assert platform.python_version() not in content
    assert set(response.context["themes"]) >= {"mail2003", "mail2000"}
    assert response.context["next_url"] == "/dev/inbox/"


def test_settings_requires_permission(client, db):
    assert client.get(reverse("postbox:settings")).status_code == 302


def test_choosing_a_theme_sets_cookie_and_renders_it(staff_client, storage, settings):
    settings.POSTBOX_THEME = "mail2003"
    response = staff_client.post(
        reverse("postbox:settings"), {"theme": "mail2000", "next": "/dev/inbox/"}
    )
    assert response.status_code == 302
    assert response.url == "/dev/inbox/"
    cookie = response.cookies["postbox_theme"]
    assert cookie.value == "mail2000"
    assert cookie["path"] == reverse("postbox:overview")

    content = staff_client.get(reverse("postbox:overview")).content.decode()
    assert "themes/mail2000.css" in content
    assert "themes/mail2003.css" not in content


def test_unknown_theme_is_ignored(staff_client, storage, settings):
    settings.POSTBOX_THEME = "mail2003"
    response = staff_client.post(reverse("postbox:settings"), {"theme": "../../evil"})
    assert "postbox_theme" not in response.cookies

    staff_client.cookies["postbox_theme"] = "../../evil"
    content = staff_client.get(reverse("postbox:overview")).content.decode()
    assert "themes/mail2003.css" in content
    assert "evil" not in content


def test_settings_never_redirects_off_site(staff_client, storage):
    response = staff_client.post(
        reverse("postbox:settings"),
        {"theme": "mail2003", "next": "https://evil.example/"},
    )
    assert response.url == reverse("postbox:overview")


def test_random_mails_give_each_person_their_own_inbox():
    import random

    from tests.project.management.commands.send_test_mails import random_mails

    mails = random_mails(10, random.Random(1))
    people = {mail.to[0] for mail in mails}
    assert len(people) == 10
    assert len({mail.subject for mail in mails}) > 50
    assert random_mails(10, random.Random(1))[0].subject == mails[0].subject
