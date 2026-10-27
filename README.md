<p align="center">
  <a href="https://terminalkitten.github.io/django-postbox/">
    <img src="https://raw.githubusercontent.com/terminalkitten/django-postbox/main/src/django_postbox/static/postbox/logo.svg" alt="Postbox logo" width="72" height="72">
  </a>
</p>

<h1 align="center">django-postbox</h1>

<p align="center">
  <strong>See every mail your Django project sends, in an inbox per address.</strong><br>
  For local development, review apps and staging: read password resets, invites and receipts<br>
  the way your users will, with HTML, text, headers and attachments. No SMTP server needed.
</p>

<p align="center">
  <a href="https://terminalkitten.github.io/django-postbox/"><strong>Documentation</strong></a> ·
  <a href="https://terminalkitten.github.io/django-postbox/getting-started/">Getting started</a> ·
  <a href="https://terminalkitten.github.io/django-postbox/guides/capture-and-forward/">Capture and forward</a> ·
  <a href="https://terminalkitten.github.io/django-postbox/guides/permissions/">Permissions</a> ·
  <a href="https://terminalkitten.github.io/django-postbox/guides/themes/">Themes</a> ·
  <a href="https://pypi.org/project/django-postbox/">PyPI</a>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/terminalkitten/django-postbox/main/docs/img/inbox-mail2000.png" alt="An inbox with the newsletter mail open, mail2000 theme" width="800">
</p>

Your project sends mail: password resets, invites, order confirmations. While you build them, you want to see them the way your users will, without anything leaving your laptop or test server.

Postbox is a Django email backend that catches every mail and gives **each recipient their own inbox**. Open `/dev/inbox/`, click `alice@example.com`, and read exactly what Alice got: HTML, plain text, headers and attachments.

- **An inbox per person.** To, Cc and Bcc each get their own copy.
- **Live.** New mail shows up within five seconds, without reloading.
- **Safe.** Mail HTML is [sandboxed](https://terminalkitten.github.io/django-postbox/reference/how-it-works/), and only staff can [open the inbox](https://terminalkitten.github.io/django-postbox/guides/permissions/) by default.
- **Fits your setup.** [Pass mail on](https://terminalkitten.github.io/django-postbox/guides/capture-and-forward/) to the console or SMTP, and [keep it](https://terminalkitten.github.io/django-postbox/guides/storages/) in the database, memory or a cache.
- **[Four themes](https://terminalkitten.github.io/django-postbox/guides/themes/)**, no build step, no CDN.

Works with Python 3.11 to 3.14 and Django 5.2, 6.0 and 6.1.

## Quick start

The short version of the [Getting started](https://terminalkitten.github.io/django-postbox/getting-started/) tutorial.

### 1. Install

```bash
pip install django-postbox
```

### 2. Add the app and send your mail through Postbox

On **Django 6.1+**, with named mailers:

```python
# settings.py

INSTALLED_APPS = [
    # ...
    "django_postbox",
]

MAILERS = {
    "default": {
        "BACKEND": "django_postbox.backends.EmailBackend",
        # Optional: also print every mail in the terminal
        "OPTIONS": {"forward_to": "console"},
    },
    "console": {
        "BACKEND": "django.core.mail.backends.console.EmailBackend",
    },
}
```

On **Django 5.2 and 6.0**, replace `MAILERS` with:

```python
# settings.py

EMAIL_BACKEND = "django_postbox.backends.EmailBackend"

# Optional: also print every mail in the terminal
POSTBOX_FORWARD_BACKEND = "django.core.mail.backends.console.EmailBackend"
```

### 3. Add the inbox to your URLs

```python
# urls.py

from django.conf import settings
from django.urls import include, path

urlpatterns = [
    # ...
]

if settings.DEBUG:
    urlpatterns += [path("dev/inbox/", include("django_postbox.urls"))]
```

> [!TIP]
> The inbox is for staff only, so visitors go to your login page first. No login page yet? Add `LOGIN_URL = "admin:login"` to your settings to use the admin login. To let others in, see [Who can read the inbox](https://terminalkitten.github.io/django-postbox/guides/permissions/).

### 4. Migrate and create a staff user

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 5. Send a mail

```bash
python manage.py shell
```

```pycon
>>> from django.core.mail import send_mail
>>> send_mail("Hello", "Hi Alice", "me@example.com", ["alice@example.com"])
1
```

### 6. Open the inbox

```bash
python manage.py runserver
```

Go to http://127.0.0.1:8000/dev/inbox/, log in, and Alice's inbox is waiting for you.

## Themes

Pick a default with `POSTBOX_THEME`, and everyone can choose their own under **Options** in the inbox. You can also [write your own theme](https://terminalkitten.github.io/django-postbox/guides/themes/#write-your-own-theme) in one CSS file.

| `mail2003` (default) | `mail2000` |
| --- | --- |
| ![Inbox, mail2003 theme](https://raw.githubusercontent.com/terminalkitten/django-postbox/main/docs/img/inbox-mail2003.png) | ![Inbox, mail2000 theme](https://raw.githubusercontent.com/terminalkitten/django-postbox/main/docs/img/inbox-mail2000.png) |
| **`mail2010`** | **`modern`** |
| ![Inbox, mail2010 theme](https://raw.githubusercontent.com/terminalkitten/django-postbox/main/docs/img/inbox-mail2010.png) | ![Inbox, modern theme](https://raw.githubusercontent.com/terminalkitten/django-postbox/main/docs/img/inbox-modern.png) |

## Documentation

The [documentation](https://terminalkitten.github.io/django-postbox/) walks you through everything beyond the quick start:

- [Capture and forward](https://terminalkitten.github.io/django-postbox/guides/capture-and-forward/): print mail to the terminal, deliver for real and keep a copy, keep your own domain out of the inbox
- [Who can read the inbox](https://terminalkitten.github.io/django-postbox/guides/permissions/): staff, a QA group, or everyone while debugging
- [Where mail is kept](https://terminalkitten.github.io/django-postbox/guides/storages/): database, memory or a shared cache
- [Themes](https://terminalkitten.github.io/django-postbox/guides/themes/): the four looks and writing your own
- [How it works](https://terminalkitten.github.io/django-postbox/reference/how-it-works/): how mail is stored and shown safely
- [Settings](https://terminalkitten.github.io/django-postbox/reference/settings/): every setting and when to change it

## Development

See [Working on Postbox](https://terminalkitten.github.io/django-postbox/guides/development/) for the full guide.

```bash
uv sync
make migrate           # the test project in tests/project
uv run python manage.py createsuperuser
make mail              # send demo mail to ten random people
make rs                # http://127.0.0.1:8000/dev/inbox/

make lint              # ruff, ty and pytest
uv run tox             # every Python and Django version
make docs-serve        # the docs, reloading as you edit
make screenshots       # rebuild docs/img in every theme
make htmx              # update the bundled htmx
```
