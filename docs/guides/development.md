---
title: Development
description: Run the test project, the tests and the docs locally.
sidebar:
  order: 5
---

```bash
uv sync
make migrate        # creates db/postbox.db for the test project in tests/project
make mail           # sends a few test mails
make rs             # http://127.0.0.1:8000/dev/inbox/ (create a superuser first)
make lint           # ruff, ty and pytest
uv run tox          # every supported Python and Django version
make docs-serve     # these docs with live reload
make screenshots    # rebuild the screenshots in docs/img with headless Chrome
```
