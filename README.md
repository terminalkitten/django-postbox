<p align="center">
  <a href="https://terminalkitten.github.io/django-postbox/">
    <img src="https://raw.githubusercontent.com/terminalkitten/django-postbox/main/public/logo.svg" alt="Postbox logo" width="72" height="72">
  </a>
</p>

<h1 align="center">django-postbox</h1>

<p align="center">
  <strong>Catch outgoing Django mail and browse it per address, like a real inbox.</strong><br>
  For local development and review apps: every mail your project sends lands in an inbox<br>
  per recipient, with HTML, text, headers, raw source and attachments. No SMTP server needed.
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/terminalkitten/django-postbox/main/docs/img/inbox-mail2000.png" alt="An inbox with the newsletter mail open, mail2000 theme" width="800">
</p>

- **An inbox per address.** To, Cc and Bcc each get their own copy, browsable at `/dev/inbox/`.
- **Stackable backend.** Capture, then forward to the next backend (console, SMTP, ...).
- **Skip domains.** Never capture mail to e.g. your own company domain, only forward it.
- **Permission classes.** DRF-style, from settings. Staff only by default.
- **Database, in-memory or cache storage.**
- **htmx + hand-written CSS**, bundled, with no build step.

Supports Python 3.11–3.14 and Django 5.2, 6.0 and 6.1 (including the new `MAILERS` setting).

## Themes

| `mail2000` | `mail2003` (default) |
| --- | --- |
| ![Overview, mail2000 theme](https://raw.githubusercontent.com/terminalkitten/django-postbox/main/docs/img/overview-mail2000.png) | ![Overview, mail2003 theme](https://raw.githubusercontent.com/terminalkitten/django-postbox/main/docs/img/overview-mail2003.png) |
| ![Inbox search, mail2000 theme](https://raw.githubusercontent.com/terminalkitten/django-postbox/main/docs/img/search-mail2000.png) | ![Order mail, mail2003 theme](https://raw.githubusercontent.com/terminalkitten/django-postbox/main/docs/img/order-mail2003.png) |

## Quick start

```python
INSTALLED_APPS = [..., "django_postbox"]

# Django 6.1+
MAILERS = {
    "default": {
        "BACKEND": "django_postbox.backends.EmailBackend",
        "OPTIONS": {"forward_to": "console"},
    },
    "console": {"BACKEND": "django.core.mail.backends.console.EmailBackend"},
}

# Django 5.2 / 6.0
EMAIL_BACKEND = "django_postbox.backends.EmailBackend"
POSTBOX_FORWARD_BACKEND = "django.core.mail.backends.console.EmailBackend"

POSTBOX_SKIP_DOMAINS = ["company.com"]
```

```python
# urls.py
urlpatterns += [path("dev/inbox/", include("django_postbox.urls"))]
```

```bash
python manage.py migrate django_postbox
```

The full documentation is in [`docs/`](docs/index.md) and builds with [dokk](https://pypi.org/project/dokk/): `make docs-serve`.

## Development

```bash
uv sync
make migrate mail rs   # test project in tests/project, http://127.0.0.1:8000/dev/inbox/
make lint              # ruff, ty, pytest
uv run tox             # Python × Django matrix
make htmx              # update the bundled htmx
make screenshots       # rebuild docs/img/*.png with headless Chrome
```
