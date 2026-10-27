---
title: Settings
description: Every Django Postbox setting with its default.
sidebar:
  order: 1
---

All settings are optional and read when they are used, so `override_settings` works in tests.

| Setting | Default | Description |
| ------- | ------- | ----------- |
| `POSTBOX_FORWARD_BACKEND` | `None` | Dotted path of the next backend. On Django 6.1+ use the `forward_to` option in `MAILERS` |
| `POSTBOX_STORAGE` | `"django_postbox.storages.DatabaseStorage"` | Where captured mail lives, see [Storages](../guides/storages.md) |
| `POSTBOX_CACHE` | `"default"` | Cache alias for `CacheStorage` |
| `POSTBOX_SKIP_DOMAINS` | `()` | Domains (and their subdomains) that are never captured, only forwarded |
| `POSTBOX_PERMISSIONS` | `("django_postbox.permissions.IsStaff",)` | Permission classes or dotted paths, see [Permissions](../guides/permissions.md) |
| `POSTBOX_THEME` | `"mail2003"` | `"mail2003"`, `"mail2000"`, `"mail2010"`, `"modern"`, your own `postbox/themes/<name>.css`, or `None` for the plain base. Viewers can override it per browser under Options, see [Assets and templates](../guides/assets.md) |
| `POSTBOX_LOAD_HTMX` | `True` | Load the bundled htmx. Turn it off when your project provides htmx itself |

## Backend options (Django 6.1+ `MAILERS`)

| Option | Description |
| ------ | ----------- |
| `forward_to` | Alias of the mailer that receives every message after capture |
