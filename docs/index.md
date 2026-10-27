---
title: Django Postbox
description: See every mail your Django project sends, in an inbox per address, without sending anything.
---

::image[An inbox with the newsletter mail open, modern theme]{src="img/inbox-modern.png"}

Your project sends mail: password resets, invites, order confirmations, weekly digests. While you build those, you want to see them the way your users will, without real mail leaving your laptop or a test server.

**Django Postbox** catches every mail your project sends and gives each recipient their own inbox. Open `/dev/inbox/`, click `alice@example.com`, and read exactly what Alice got: the HTML, the plain text, the headers and the attachments.

## When it helps

::::cards
:::card[Building mail templates]
Change a template, send the mail again, and the inbox shows it within five seconds. No mail client, no SMTP server.
:::

:::card[Testing flows with many people]
Sign up three users, invite two of them and reset a password. Every person gets their own inbox, so you see who received what, Cc and Bcc included.
:::

:::card[Review and staging servers]
Testers read their mail in the browser, and nothing reaches your real customers. See [Capture and forward](guides/capture-and-forward.md).
:::
::::

## How it works

:::steps
1. **Your code sends mail** the way it always does: `send_mail()`, `EmailMessage.send()`, Django's password reset, a third party app.
2. **Postbox stores a copy per recipient.** It is a regular Django email backend, so nothing in your code changes.
3. **Optionally, it passes the mail on** to the next backend, for example the console or SMTP.
4. **You read it in the browser**, in one of four themes, at the URL you choose.
:::

:::caution[Not for production inboxes]
Captured mail contains password reset links and other secrets. Keep the inbox for development, test and staging servers, and keep its URL behind a login: it is staff only by default.
:::

::linkbutton[Get started]{href="getting-started/index.md"}
::linkbutton[See the themes]{href="guides/themes.md" variant="secondary"}
