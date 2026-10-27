---
title: Where mail is kept
description: Choose between the database, memory and cache storage for captured mail.
sidebar:
  order: 3
---

Postbox keeps captured mail in the **database** by default. That works almost everywhere, so you can usually skip this page. Read on when you send mail from several processes without a shared database, or want nothing written to disk.

| | Database | Memory | Cache |
| --- | --- | --- | --- |
| Mail from shells, workers and Celery | yes | no | yes, with Redis or Memcached |
| Survives a restart | yes | no | depends on the cache |
| Needs a migration | yes | no | no |
| Best for | everyday development | quick experiments | servers without the Postbox table |

Pick one with `POSTBOX_STORAGE`:

```python title="settings.py"
POSTBOX_STORAGE = "django_postbox.storages.DatabaseStorage"  # default
```

## Database

The default. Mail sent from anywhere that uses your database, `runserver`, `manage.py shell`, a Celery worker, all lands in the same inbox and stays there until you clear it.

## Memory

```python title="settings.py"
POSTBOX_STORAGE = "django_postbox.storages.MemoryStorage"
```

Mail lives in the memory of one process. It is gone when the process stops, and mail sent from another process, like a Celery worker, never shows up. Good for a quick look, not for daily work.

## Cache

```python title="settings.py"
POSTBOX_STORAGE = "django_postbox.storages.CacheStorage"
POSTBOX_CACHE = "default"  # an alias from CACHES
```

Use a shared cache such as Redis or Memcached, and every process sees the same mail without a database table.

:::tip
Django's local-memory cache is per process, just like the memory storage. Use a shared cache backend to get the benefit.
:::

:::details[Why the database is the safer choice under load]
Django caches cannot list their keys, so the cache storage keeps one index of all mail, guarded by a short lock. When many processes send at the same moment, an entry can get lost, which hides that mail from the inbox. The database storage has no such limit.
:::

## Your own storage

Store mail anywhere else by subclassing `django_postbox.storages.BaseStorage` and implementing `save`, `messages`, `get` and `delete`. Then point `POSTBOX_STORAGE` at your class. Clearing an inbox and the inbox overview build on those four methods, so they work right away.
