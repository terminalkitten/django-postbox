from pathlib import Path

import django

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = "django-postbox-test-project"
DEBUG = True
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_postbox",
    "tests.project",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "tests.project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db" / "postbox.db",
        "TEST": {"NAME": ":memory:"},
    },
}

USE_TZ = True
STATIC_URL = "static/"
LOGIN_URL = "admin:login"

if django.VERSION >= (6, 1):
    MAILERS = {
        "default": {
            "BACKEND": "django_postbox.backends.EmailBackend",
            "OPTIONS": {"forward_to": "console"},
        },
        "console": {"BACKEND": "django.core.mail.backends.console.EmailBackend"},
    }
else:
    EMAIL_BACKEND = "django_postbox.backends.EmailBackend"
    POSTBOX_FORWARD_BACKEND = "django.core.mail.backends.console.EmailBackend"

POSTBOX_SKIP_DOMAINS = ["skip.example"]
POSTBOX_THEME = "mail2000"
