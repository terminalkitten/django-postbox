---
title: Assets and templates
description: The bundled htmx and CSS, and how to override them.
sidebar:
  order: 4
---

The pages load their assets through `{% postbox_assets %}`. All of them ship with the package, so nothing comes from a CDN and there is no build step:

- `postbox/postbox.css`: layout and structure only, plus CSS variables with plain defaults
- `postbox/themes/<POSTBOX_THEME>.css`: the look. Bundled: `mail2003` (default, webmail circa 2003) and `mail2000` (classic 2000 desktop)
- `postbox/htmx.min.js`

## Themes

A theme is one stylesheet that overrides the variables from `postbox.css` (`--pb-bg`, `--pb-accent`, `--pb-font`, ...) and adds its own skin on top of the same class names. To add one, put `postbox/themes/<name>.css` in any static folder and set:

```python
POSTBOX_THEME = "<name>"
```

`POSTBOX_THEME = None` gives the plain base without a theme.

If your project already loads htmx, set `POSTBOX_LOAD_HTMX = False` and add it yourself in an overridden `postbox/base.html` (`{% block extra_head %}`).

## Updating htmx

```bash
make htmx
```

This runs `scripts/update_htmx.py`, which downloads the latest htmx release from npm into `src/django_postbox/static/postbox/htmx.min.js`. Commit the result.

## How the pages use htmx

- `hx-boost` on the body makes links and forms swap the page without a reload.
- The inbox list and the overview poll every five seconds and only swap themselves (`hx-select`).
- The HTML body is rendered in `<iframe sandbox srcdoc>`: no scripts, and neither postbox's CSS nor the mail's CSS leaks across. A CSP in the mail's head only lets images, styles and fonts load, and links open in a new tab.
