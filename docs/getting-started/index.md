---
title: Getting started
description: Add Django Postbox to a project, send a mail and read it in its inbox, step by step.
sidebar:
  order: 1
---

You need Python 3.11 to 3.14 and Django 5.2, 6.0 or 6.1 (Django 6 needs Python 3.12+). Every step below was run on a fresh `django-admin startproject` with Django 6.1 and 5.2.

:::steps
1. **Install the package**

   ```bash
   pip install django-postbox
   ```

2. **Add the app** to `settings.py`:

   ```python
   INSTALLED_APPS = [
       ...
       "django_postbox",
   ]
   ```

3. **Route your mail through postbox.** On Django 6.1+ with `MAILERS`:

   ```python
   MAILERS = {
       "default": {
           "BACKEND": "django_postbox.backends.EmailBackend",
           "OPTIONS": {"forward_to": "console"},  # optional: also print every mail
       },
       "console": {"BACKEND": "django.core.mail.backends.console.EmailBackend"},
   }
   ```

   On Django 5.2 and 6.0:

   ```python
   EMAIL_BACKEND = "django_postbox.backends.EmailBackend"
   POSTBOX_FORWARD_BACKEND = "django.core.mail.backends.console.EmailBackend"  # optional
   ```

   Without a forward backend, mail is only captured and never leaves your machine.

4. **Mount the inbox** in your root `urls.py`, only in development:

   ```python
   from django.conf import settings
   from django.urls import include, path

   if settings.DEBUG:
       urlpatterns += [path("dev/inbox/", include("django_postbox.urls"))]
   ```

   The inbox is for staff only. If your project has no login page of its own yet, let Django send visitors to the admin login, in `settings.py`:

   ```python
   LOGIN_URL = "admin:login"
   ```

5. **Create the tables**, all of them: the inbox needs Django's auth and sessions too.

   ```bash
   python manage.py migrate
   ```

6. **Create a staff user** to log in with, if you have none yet:

   ```bash
   python manage.py createsuperuser
   ```

7. **Send a test mail:**

   ```bash
   python manage.py shell -c "from django.core.mail import send_mail; send_mail('Hello', 'Hi Alice', 'me@example.com', ['alice@example.com'])"
   ```

   With the console forward from step 3 you also see the mail printed in your terminal.

8. **Open the inbox:**

   ```bash
   python manage.py runserver
   ```

   Go to [http://127.0.0.1:8000/dev/inbox/](http://127.0.0.1:8000/dev/inbox/) and log in. `alice@example.com` is listed; click it to read the mail.
:::

The overview and the inbox refresh every five seconds, so mail you send now shows up without reloading.

## Next steps

- Keep mail to your own domain out of the inbox with [skip domains](../guides/backend.md#skip-domains): `POSTBOX_SKIP_DOMAINS = ["company.com"]`.
- Pick a look with `POSTBOX_THEME = "mail2000"` or keep the default `"mail2003"`, see [Assets and templates](../guides/assets.md).
- Decide who may read captured mail with [Permissions](../guides/permissions.md). It is staff only by default.
- Choose where mail is kept in [Storages](../guides/storages.md): database (default), memory or cache.
