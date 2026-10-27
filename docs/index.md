---
title: Django Postbox
description: Catch outgoing Django mail and browse it per address, like a real inbox.
---

::image[An inbox with the newsletter mail open, mail2000 theme]{src="img/inbox-mail2000.png"}

**Django Postbox** is an email backend plus a small htmx app. Every mail your project sends during development is captured and shown per recipient, at `/dev/inbox/` or wherever you mount it.

- **An inbox per address.** Each recipient (To, Cc and Bcc) gets their own copy, so you see exactly what `alice@example.com` received.
- **Stackable.** Postbox captures the mail, then passes it on to the next backend: console, SMTP, anything.
- **Skip domains.** Mail to domains such as your own company is never captured, only passed on.
- **Permission classes.** DRF-style classes in settings decide who can open the inbox. Staff only by default.
- **Three storages.** Database (default), in-memory or the Django cache.
- **No build step.** Hand-written CSS and a bundled htmx file.

Continue with [Getting started](getting-started/index.md).
