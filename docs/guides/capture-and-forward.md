---
title: Capture and forward
description: Choose what Postbox keeps and where mail goes next, with a recipe for each setup.
sidebar:
  order: 1
---

Postbox is a regular Django email backend. For every message your project sends, it does two things:

1. **It keeps a copy for every recipient**: To, Cc and Bcc. Each address gets its own inbox, so `alice@example.com` and `bob@example.com` each see the mail as they received it.
2. **It passes the message on**, if you tell it where to. Otherwise the mail stops here.

Pick the recipe that matches your situation.

## Keep everything on your machine

This is the default. With no next backend, Postbox is the end of the line: you read the mail in the inbox, and nobody else ever gets it.

::::tabs{sync="django"}
:::tab[Django 6.1+]
```python title="settings.py"
MAILERS = {
    "default": {"BACKEND": "django_postbox.backends.EmailBackend"},
}
```
:::

:::tab[Django 5.2 and 6.0]
```python title="settings.py"
EMAIL_BACKEND = "django_postbox.backends.EmailBackend"
```
:::
::::

This is what you want on your laptop, and on review or staging servers where testers sign up with real-looking addresses.

## Also print every mail in the terminal

Handy when you work in the terminal anyway: the mail shows up in the inbox *and* in your `runserver` output.

::::tabs{sync="django"}
:::tab[Django 6.1+]
```python title="settings.py" {4}
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
:::

:::tab[Django 5.2 and 6.0]
```python title="settings.py" {2}
EMAIL_BACKEND = "django_postbox.backends.EmailBackend"
POSTBOX_FORWARD_BACKEND = "django.core.mail.backends.console.EmailBackend"
```
:::
::::

`forward_to` names another entry in `MAILERS`. `POSTBOX_FORWARD_BACKEND` is the dotted path of any email backend.

## Deliver for real and keep a copy

Forward to SMTP and Postbox becomes a logbook: everyone gets their mail as usual, and you can still look up what was sent.

```python title="settings.py"
MAILERS = {
    "default": {
        "BACKEND": "django_postbox.backends.EmailBackend",
        "OPTIONS": {"forward_to": "smtp"},
    },
    "smtp": {
        "BACKEND": "django.core.mail.backends.smtp.EmailBackend",
        "OPTIONS": {"host": "smtp.example.com", "port": 587, "use_tls": True},
    },
}
```

:::danger[Every message is forwarded]
Postbox passes on *every* message, also the ones it captured. Never forward to a real SMTP server on a test server with real customer addresses in its database: they would get your test mail.
:::

## Keep some mail out of the inbox

Some mail is noise in the inbox, like error reports to your own team. List those domains and Postbox will not keep a copy:

```python title="settings.py"
POSTBOX_SKIP_DOMAINS = ["company.com"]
```

Subdomains count too, so `eu.company.com` is skipped as well. A mail to both `dev@company.com` and `alice@example.com` still lands in Alice's inbox, only the copy for `company.com` is left out.

:::note
Skipping only decides what Postbox *keeps*. Whether the mail goes anywhere is still up to the forward: with a forward the skipped mail is delivered, without one it is dropped.
:::

## When storing fails

If Postbox cannot store a mail, for example because the database is down, you get the error, just like with any other backend. Sending with `fail_silently=True` ignores it, on Django versions that still support that argument.

:::details[What about a loop?]
A forward that points back at Postbox would send every mail around forever. Postbox refuses to start instead, with an `ImproperlyConfigured` error that tells you so.
:::
