import uuid

from django_postbox.storages import StoredMessage, hash_address


def stored(recipient="alice@example.com", subject="Hi"):
    raw = f"Subject: {subject}\nTo: {recipient}\n\nbody\n".encode()
    return StoredMessage(
        recipient=recipient, sender="me@example.com", subject=subject, raw=raw
    )


def test_hash_address_ignores_case_and_whitespace():
    assert hash_address(" Alice@Example.com ") == hash_address("alice@example.com")
    assert len(hash_address("alice@example.com")) == 16


def test_save_get_list_delete(storage):
    first, second, other = (
        stored(subject="one"),
        stored(subject="two"),
        stored("bob@example.com"),
    )
    for message in (first, second, other):
        storage.save(message)

    assert storage.get(first.id).subject == "one"
    assert storage.get(uuid.uuid4()) is None
    assert [m.subject for m in storage.messages(first.hash)] == ["two", "one"]
    assert len(storage.messages()) == 3

    storage.delete(first.id)
    assert storage.get(first.id) is None
    assert len(storage.messages()) == 2


def test_inboxes_grouped_newest_first(storage):
    storage.save(stored("alice@example.com", subject="Older"))
    storage.save(stored("bob@example.com"))
    storage.save(stored("alice@example.com", subject="Newest"))

    inboxes = storage.inboxes()
    assert [(inbox.address, inbox.count) for inbox in inboxes] == [
        ("alice@example.com", 2),
        ("bob@example.com", 1),
    ]
    assert inboxes[0].hash == hash_address("alice@example.com")
    assert inboxes[0].last_subject == "Newest"


def test_clear_one_inbox_or_all(storage):
    alice, bob = stored("alice@example.com"), stored("bob@example.com")
    storage.save(alice)
    storage.save(bob)

    storage.clear(alice.hash)
    assert [m.recipient for m in storage.messages()] == ["bob@example.com"]
    storage.clear()
    assert storage.messages() == []


def test_parsed_parts(storage, send, welcome):
    send(welcome)
    message = storage.messages()[0]
    assert message.text.rstrip() == "Hi Alice"
    assert message.html.startswith("<h1>Hi Alice</h1>")
    assert [(a.filename, a.content) for a in message.attachments] == [
        ("notes.bin", b"notes")
    ]
    assert ("Subject", "Welcome") in message.headers
    assert "Subject: Welcome" in message.raw_text
