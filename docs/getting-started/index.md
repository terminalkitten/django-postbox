---
title: Getting started
description: Add Django Postbox to your project, send a mail and read it in its own inbox.
sidebar:
  order: 1
---

In ten minutes you will send a mail from your project and read it in an inbox in your browser. You need Python 3.11 to 3.14 and Django 5.2, 6.0 or 6.1 (Django 6 needs Python 3.12+).

:::::steps
1. **Install the package.**

   ::install[django-postbox]{tools="pip uv"}

2. **Add the app.**

   ```python title="settings.py"
   INSTALLED_APPS = [
       # ...
       "django_postbox",
   ]
   ```

3. **Send your mail through Postbox.** Django 6.1 introduced named mailers, older versions use a single backend setting:

   ::::tabs{sync="django"}
   :::tab[Django 6.1+]
   ```python title="settings.py"
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
   :::

   :::tab[Django 5.2 and 6.0]
   ```python title="settings.py"
   EMAIL_BACKEND = "django_postbox.backends.EmailBackend"

   # Optional: also print every mail in the terminal
   POSTBOX_FORWARD_BACKEND = "django.core.mail.backends.console.EmailBackend"
   ```
   :::
   ::::

   Without the forward, mail stops at Postbox and never leaves your machine.

4. **Add the inbox to your URLs**, only while developing:

   ```python title="urls.py"
   from django.conf import settings
   from django.urls import include, path

   urlpatterns = [
       # ...
   ]

   if settings.DEBUG:
       urlpatterns += [path("dev/inbox/", include("django_postbox.urls"))]
   ```

   :::tip
   The inbox is for staff only, so visitors are sent to your login page first. A new project has none yet: add `LOGIN_URL = "admin:login"` to `settings.py` to use the admin login.
   :::

5. **Create the tables and a staff user.** The inbox needs Django's auth and session tables too, so run all migrations:

   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Send a mail.** Any mail your project sends ends up in Postbox. To try it right away, open a shell:

   ```bash
   python manage.py shell
   ```

   ```pycon
   >>> from django.core.mail import send_mail
   >>> send_mail("Hello", "Hi Alice", "me@example.com", ["alice@example.com"])
   1
   ```

7. **Open the inbox.**

   ```bash
   python manage.py runserver
   ```

   Go to [http://127.0.0.1:8000/dev/inbox/](http://127.0.0.1:8000/dev/inbox/) and log in. Alice's inbox is waiting for you.
:::::

::image[The overview with an inbox per address]{src="../img/overview-modern.png" caption="Every address that received mail gets its own inbox."}

Leave the page open while you work: the overview and the inbox refresh every five seconds, so new mail shows up by itself.

## Where to next

::::cards
:::card[Capture and forward]{href="../guides/capture-and-forward.md"}
Also print mail to the console, or keep your own domain out of the inbox.
:::

:::card[Who can read the inbox]{href="../guides/permissions.md"}
Open it to a QA group, or to everyone on a review server.
:::

:::card[Themes]{href="../guides/themes.md"}
Pick one of four looks, or write your own in one CSS file.
:::
::::
