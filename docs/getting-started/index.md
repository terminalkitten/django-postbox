---
title: Getting started
description: Install Django Postbox, route your mail through it and open the inbox.
sidebar:
  order: 1
---

You need Python 3.11 to 3.14 and Django 5.2, 6.0 or 6.1 (Django 6 needs Python 3.12+).

:::steps
1. Install the package:

   ```bash
   pip install django-postbox
   ```

2. Add the app:

   ```python
   INSTALLED_APPS = [
       ...
       "django_postbox",
   ]
   ```

3. Route your mail through postbox. On Django 6.1+ with `MAILERS`:

   ```python
   MAILERS = {
       "default": {
           "BACKEND": "django_postbox.backends.EmailBackend",
           "OPTIONS": {"forward_to": "console"},  # optional
       },
       "console": {"BACKEND": "django.core.mail.backends.console.EmailBackend"},
   }
   ```

   On Django 5.2 and 6.0:

   ```python
   EMAIL_BACKEND = "django_postbox.backends.EmailBackend"
   POSTBOX_FORWARD_BACKEND = "django.core.mail.backends.console.EmailBackend"  # optional
   ```

4. Mount the URLs, for example only in development:

   ```python
   from django.conf import settings
   from django.urls import include, path

   if settings.DEBUG:
       urlpatterns += [path("dev/inbox/", include("django_postbox.urls"))]
   ```

5. Create the table and send a mail:

   ```bash
   python manage.py migrate django_postbox
   ```
:::

Log in as a staff user and open `/dev/inbox/`. The overview lists every address that received mail, and it refreshes every five seconds.
