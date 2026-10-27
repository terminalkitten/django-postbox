---
title: Settings
description: Every Django Postbox setting, its default, and when you would change it.
sidebar:
  order: 1
---

Every setting is optional. Postbox reads them each time it needs one, so `override_settings` works in your tests.

| Setting | Default | Change it when you want to |
| --- | --- | --- |
| `POSTBOX_FORWARD_BACKEND` | `None` | pass mail on to another backend on Django 5.2 or 6.0, see [Capture and forward](../guides/capture-and-forward.md) |
| `POSTBOX_SKIP_DOMAINS` | `()` | keep mail to some domains out of the inbox, like `["company.com"]` |
| `POSTBOX_PERMISSIONS` | `("django_postbox.permissions.IsStaff",)` | let other people read the inbox, see [Who can read the inbox](../guides/permissions.md) |
| `POSTBOX_STORAGE` | `"django_postbox.storages.DatabaseStorage"` | keep mail in memory or a cache, see [Where mail is kept](../guides/storages.md) |
| `POSTBOX_CACHE` | `"default"` | use another alias from `CACHES` for the cache storage |
| `POSTBOX_THEME` | `"modern"` | start everyone on `"mail2003"`, `"mail2000"`, `"mail2010"` or your own theme, see [Themes](../guides/themes.md) |
| `POSTBOX_LOAD_HTMX` | `True` | load your project's own htmx instead of the bundled copy |

## Mailer options

On Django 6.1 and later, Postbox is configured as one of your `MAILERS`. It takes one option:

| Option | Default | Change it when you want to |
| --- | --- | --- |
| `forward_to` | none | pass every mail on to another mailer, by its alias |

```python title="settings.py"
MAILERS = {
    "default": {
        "BACKEND": "django_postbox.backends.EmailBackend",
        "OPTIONS": {"forward_to": "console"},
    },
    "console": {
        "BACKEND": "django.core.mail.backends.console.EmailBackend",
    },
}
```
