---
title: Working on Postbox
description: Run the test project, the tests and the docs, and refresh the screenshots and htmx.
sidebar:
  order: 5
---

Want to change Postbox itself? The repository has a small Django project in `tests/project` that you can run and click through.

:::steps
1. **Install** the dependencies with [uv](https://docs.astral.sh/uv/):

   ```bash
   uv sync
   ```

2. **Set up the test project** with its database, a user to log in with and a few hundred demo mails for ten random people:

   ```bash
   make migrate
   uv run python manage.py createsuperuser
   make mail
   ```

3. **Run it** and open [http://127.0.0.1:8000/dev/inbox/](http://127.0.0.1:8000/dev/inbox/):

   ```bash
   make rs
   ```
:::

## Checks

```bash
make lint      # ruff, ty and pytest with coverage
uv run tox     # every supported Python and Django version
```

## Docs and screenshots

```bash
make docs-serve    # these docs, reloading as you edit
make screenshots   # rebuild docs/img in every theme
```

`make screenshots` fills a throwaway in-memory database with demo mail, so your own test database is left alone. It needs Chrome; set `CHROME=/path/to/chrome` if it is not found.

:::note[One logo]
The logo lives in `src/django_postbox/static/postbox/logo.svg`, where the app needs it. The docs site uses it through the symlinks `public/logo.svg` and `public/favicon.svg`, and the README links to it directly. Change it there and it changes everywhere.
:::

## Update htmx

```bash
make htmx
```

This downloads the latest htmx release into `src/django_postbox/static/postbox/htmx.min.js`. Commit the result.
