---
title: Themes
description: Pick one of four looks for the inbox, let everyone choose their own, or write a theme in one CSS file.
sidebar:
  order: 4
---

The inbox comes in four looks. They change nothing but the styling, so pick the one you like to look at all day.

::::tabs{sync="theme"}
:::tab[mail2003]
::image[An inbox in the mail2003 theme]{src="../img/inbox-mail2003.png" caption="mail2003, the default: webmail around 2003, glossy blue bars on a warm tan."}
:::

:::tab[mail2000]
::image[An inbox in the mail2000 theme]{src="../img/inbox-mail2000.png" caption="mail2000: a classic 2000 desktop, grey bevels and a navy title bar."}
:::

:::tab[mail2010]
::image[An inbox in the mail2010 theme]{src="../img/inbox-mail2010.png" caption="mail2010: clean early-2010s webmail, white and flat."}
:::

:::tab[modern]
::image[An inbox in the modern theme]{src="../img/inbox-modern.png" caption="modern: rounded cards, and it follows your light or dark mode."}
:::
::::

## Choose a theme

Set the default for everyone:

```python title="settings.py"
POSTBOX_THEME = "mail2000"
```

Everyone can still pick their own under **Options**, top right in the inbox. That choice is kept in a cookie in their browser, so it sticks without touching your settings. The page is rendered with the right stylesheet from the start, so it never flashes in the wrong theme.

## Write your own theme

A theme is a single CSS file. The base stylesheet takes care of the layout and exposes its colours and fonts as CSS variables, so a theme mostly sets those.

::::steps
1. **Add the file** to a static folder of one of your apps:

   :::filetree
   - myapp/
     - static/
       - postbox/
         - themes/
           - **sunset.css** your theme
   :::

2. **Set the variables**, and add any extra styling you like on top of the `pb-` classes:

   ```css title="myapp/static/postbox/themes/sunset.css"
   :root {
     --pb-bg: #fff7ed;
     --pb-surface: #ffffff;
     --pb-text: #431407;
     --pb-muted: #9a3412;
     --pb-border: #fed7aa;
     --pb-accent: #ea580c;
     --pb-select: #ffedd5;
     --pb-select-text: #431407;
     --pb-font: Georgia, serif;
   }

   .pb-header {
     background: #ea580c;
     color: #fff;
   }
   ```

3. **Use it:**

   ```python title="settings.py"
   POSTBOX_THEME = "sunset"
   ```

   Your theme also shows up under Options, next to the bundled ones.
::::

:::tip
The bundled themes in `django_postbox/static/postbox/themes/` are the best examples: copy one and start changing colours.
:::

`POSTBOX_THEME = None` turns themes off and leaves the plain base stylesheet.

## Bring your own htmx

The inbox uses a copy of [htmx](https://htmx.org) that ships with the package, so nothing loads from a CDN. If your project already loads htmx on every page, switch the bundled copy off and load yours in an overridden `postbox/base.html` (`{% block extra_head %}`):

```python title="settings.py"
POSTBOX_LOAD_HTMX = False
```
