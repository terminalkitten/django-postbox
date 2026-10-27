---
title: Storages
description: Database, in-memory and cache storage for captured mail.
sidebar:
  order: 2
---

Set `POSTBOX_STORAGE` to one of:

| Storage | Shared between processes | Survives restart | Use for |
| ------- | ------------------------ | ---------------- | ------- |
| `django_postbox.storages.DatabaseStorage` (default) | yes | yes | normal development, mail sent from shells, workers and Celery |
| `django_postbox.storages.MemoryStorage` | no | no | a single process, quick tests |
| `django_postbox.storages.CacheStorage` | yes, with Redis or Memcached | depends on the cache | threaded or multi-process servers without a database table |

`CacheStorage` uses the cache named by `POSTBOX_CACHE` (default `"default"`). Django caches cannot list their keys, so postbox keeps an index key that is guarded by a short lock. If many processes write at once, use `DatabaseStorage`.

Every storage keeps the raw RFC 822 bytes. Postbox parses them with Python's `email` package when you open a message, so the HTML, text, headers and attachments are always what was actually sent.

## Your own storage

Subclass `django_postbox.storages.BaseStorage` and implement `save`, `messages`, `get` and `delete`. `clear` and `inboxes` work on top of those, and you can override them for speed.
