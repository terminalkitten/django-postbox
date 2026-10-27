---
title: Email backend
description: How postbox captures mail, forwards it to the next backend and skips domains.
sidebar:
  order: 1
---

`django_postbox.backends.EmailBackend` does two things for every message:

1. **Capture.** It stores one copy per recipient (To, Cc and Bcc). Addresses are lowercased, and display names are dropped.
2. **Forward.** If a next backend is configured, it hands **every** message to it, captured or not, and returns that backend's count.

With no next backend, postbox is the end of the line and nothing leaves your machine.

## Next backend

| Django | How |
| ------ | --- |
| 6.1+ with `MAILERS` | `"OPTIONS": {"forward_to": "<alias>"}` names another mailer |
| 5.2, 6.0, or 6.1 without `MAILERS` | `POSTBOX_FORWARD_BACKEND = "dotted.path.EmailBackend"` |

If the next backend is postbox itself, you get `ImproperlyConfigured` instead of an endless loop.

## Skip domains

```python
POSTBOX_SKIP_DOMAINS = ["company.com"]
```

Postbox does not capture mail to `company.com` or any of its subdomains (`eu.company.com`), but still forwards it. If a mail goes to both a skipped and a normal address, only the normal address gets a copy.

## Failures

If the storage fails, the error is raised, unless the backend was created with `fail_silently=True`.
