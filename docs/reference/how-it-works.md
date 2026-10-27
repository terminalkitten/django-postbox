---
title: How it works
description: How Postbox stores mail, shows HTML safely and keeps the inbox up to date.
sidebar:
  order: 2
---

You do not need this page to use Postbox. It explains the choices behind it, for when you wonder why something works the way it does.

## Mail is kept exactly as it was sent

Postbox stores the raw message, byte for byte, the way Django would hand it to an SMTP server. Only when you open a mail does it take it apart with Python's own `email` package. What you see in the HTML, Text, Headers and Attachments tabs is therefore what the recipient would get, and **Download .eml** gives you the original to open in any mail client.

Every recipient gets their own copy. That is why deleting a mail from Alice's inbox leaves Bob's inbox alone, and why a Bcc recipient has the mail in their inbox while nobody else can see they got it.

## HTML mail cannot touch the inbox

Mail HTML comes from your templates, often with user input in it, so Postbox treats it as untrusted:

- It is shown in a sandboxed `<iframe>`, so scripts in a mail never run.
- A Content Security Policy only lets images, styles and fonts load, so a mail cannot post forms or call home.
- Links open in a new tab instead of inside the frame.
- The mail's CSS and the inbox's CSS stay apart: you see the mail as its recipient would, and a mail cannot restyle the inbox.

## The inbox keeps itself up to date

The overview and the inbox ask the server every five seconds whether anything changed. While nothing did, the answer is an empty "204 No Content" and the page is left alone, so polling is cheap and never resets your scroll position. When new mail arrives, only the list is updated.

Moving around uses [htmx](https://htmx.org): clicking a mail or a tab replaces just the message pane, and every URL still works as a normal page, so you can bookmark or share any mail.

## The theme is chosen on the server

The theme from **Options** is kept in a `postbox_theme` cookie, valid for the inbox URLs only. The server reads it and puts the right stylesheet in the page from the start, so there is no flash of the wrong theme. Only the names of themes that exist are accepted.
