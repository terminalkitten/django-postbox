import base64
from typing import Any

from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand, CommandParser

# 1x1 blue PNG
PIXEL_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
)
TINY_PDF = b"%PDF-1.4\n1 0 obj<</Type/Catalog>>endobj\ntrailer<</Root 1 0 R>>\n%%EOF\n"

INVITE_ICS = (
    "BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//postbox//demo//EN\r\nMETHOD:REQUEST\r\n"
    "BEGIN:VEVENT\r\nUID:sprint-review@example.com\r\nDTSTART:20261029T130000Z\r\n"
    "DTEND:20261029T140000Z\r\nSUMMARY:Sprint review\r\nLOCATION:Room Pony\r\n"
    "END:VEVENT\r\nEND:VCALENDAR\r\n"
)

ORDER_HTML = """
<div style="font-family:Arial,sans-serif;max-width:560px">
  <h2 style="color:#2253c3">Thanks for your order, Alice!</h2>
  <p>Order <b>#10042</b> is on its way.</p>
  <table style="border-collapse:collapse;width:100%">
    <tr style="background:#eef3fc"><th align="left">Item</th><th>Qty</th><th align="right">Price</th></tr>
    <tr><td>Django mug</td><td align="center">2</td><td align="right">&euro; 24,00</td></tr>
    <tr><td>Pony sticker pack</td><td align="center">1</td><td align="right">&euro; 4,50</td></tr>
    <tr style="border-top:1px solid #999"><td><b>Total</b></td><td></td><td align="right"><b>&euro; 28,50</b></td></tr>
  </table>
  <p><a href="https://example.com/orders/10042/">Track your order</a></p>
</div>
"""

NEWSLETTER_HTML = f"""
<body style="margin:0;background:#f4f4f4">
  <table width="100%" cellpadding="0" cellspacing="0"><tr><td align="center">
    <table width="600" style="background:#fff;font-family:Georgia,serif">
      <tr><td style="background:#1b4332;color:#fff;padding:24px;font-size:28px">The Weekly Pony</td></tr>
      <tr><td style="padding:24px">
        <img src="data:image/png;base64,{base64.b64encode(PIXEL_PNG).decode()}" width="552" height="8" alt="" style="display:block;background:#40916c">
        <h1>Django 6.1 ships MAILERS</h1>
        <p>Named mailers, like CACHES and DATABASES. Here is what changes for your project.</p>
        <p style="text-align:center"><a href="https://example.com/read" style="background:#40916c;color:#fff;padding:10px 18px;text-decoration:none">Read more</a></p>
      </td></tr>
      <tr><td style="padding:12px 24px;color:#888;font-size:12px">You get this because you subscribed. <a href="https://example.com/unsubscribe">Unsubscribe</a></td></tr>
    </table>
  </td></tr></table>
</body>
"""


def build(
    subject: str,
    to: list[str],
    text: str,
    html: str | None = None,
    attachments: tuple[tuple[str, Any, str], ...] = (),
    **kwargs: Any,
) -> EmailMultiAlternatives:
    message = EmailMultiAlternatives(
        subject=subject,
        body=text,
        from_email=kwargs.pop("from_email", "Postbox Demo <noreply@example.com>"),
        to=to,
        **kwargs,
    )
    if html:
        message.attach_alternative(html, "text/html")
    for attachment in attachments:
        message.attach(*attachment)
    return message


def demo_mails() -> list[EmailMultiAlternatives]:
    return [
        build(
            "Welcome to Postbox",
            ["alice@example.com"],
            "Hi Alice,\n\nThis is the plain text part.",
            "<h1 style='color:#2253c3'>Hi Alice</h1><p>This is the <b>HTML</b> part.</p>",
            attachments=(("notes.txt", "Some attached notes.\n", "text/plain"),),
            cc=["bob@example.com"],
        ),
        build(
            "Reset your password",
            ["Alice <alice@example.com>"],
            "Reset here: https://example.com/reset/abc123/\n\nNot you? Ignore this mail.",
            bcc=["audit@example.com"],
        ),
        build(
            "Your order #10042 has shipped",
            ["alice@example.com"],
            "Order #10042: 2x Django mug, 1x Pony sticker pack. Total EUR 28,50.",
            ORDER_HTML,
            attachments=(("invoice-10042.pdf", TINY_PDF, "application/pdf"),),
            from_email="Shop <orders@shop.example>",
        ),
        build(
            "The Weekly Pony #42",
            ["alice@example.com", "bob@example.com", "dave@example.org"],
            "Django 6.1 ships MAILERS. Read more: https://example.com/read",
            NEWSLETTER_HTML,
            from_email="The Weekly Pony <news@pony.example>",
            reply_to=["editor@pony.example"],
        ),
        build(
            "Café menu ☕ — prix fixe €19",
            ["zoë@example.com"],
            "Bonjour Zoë,\n\nCrème brûlée is back on the menu. À bientôt!",
            "<p>Bonjour <b>Zoë</b>,</p><p>Crème brûlée is back on the menu. À bientôt! 🍮</p>",
        ),
        build(
            "Your photo was uploaded",
            ["bob@example.com"],
            "Your photo is attached.",
            attachments=(("pixel.png", PIXEL_PNG, "image/png"),),
        ),
        build(
            "[ERROR] Internal Server Error: /checkout/",
            ["ops@example.com"],
            "Traceback (most recent call last):\n"
            '  File "shop/views.py", line 42, in checkout\n'
            "    total = cart.total / cart.count\n"
            "ZeroDivisionError: division by zero\n",
            from_email="root@localhost",
        ),
        build(
            "Meeting notes: release planning",
            ["team@example.com"],
            "\n".join(
                f"{number}. Decision number {number} about the release."
                for number in range(1, 61)
            ),
            cc=["alice@example.com", "bob@example.com"],
        ),
        # A short thread between Alice and Bob
        build(
            "Lunch on Friday?",
            ["alice@example.com"],
            "Hey Alice,\n\nPizza at Luigi's on Friday, 12:30?\n\nBob",
            from_email="Bob <bob@example.com>",
            headers={"Message-ID": "<lunch-1@example.com>"},
        ),
        build(
            "Re: Lunch on Friday?",
            ["bob@example.com"],
            "Sounds great, see you there!\n\n> Pizza at Luigi's on Friday, 12:30?",
            from_email="Alice <alice@example.com>",
            headers={
                "In-Reply-To": "<lunch-1@example.com>",
                "References": "<lunch-1@example.com>",
            },
        ),
        build(
            "Invitation: Sprint review @ Thu 14:00",
            ["alice@example.com", "bob@example.com", "dave@example.org"],
            "You are invited to the sprint review, Thursday 14:00-15:00, room Pony.",
            "<p>You are invited to the <b>sprint review</b>.</p>"
            "<table><tr><td><b>When</b></td><td>Thursday 14:00 - 15:00</td></tr>"
            "<tr><td><b>Where</b></td><td>Room Pony</td></tr></table>"
            "<p><a href='https://example.com/rsvp?yes'>Yes</a> · <a href='https://example.com/rsvp?no'>No</a></p>",
            attachments=(("invite.ics", INVITE_ICS, "text/calendar"),),
            from_email="Calendar <calendar@example.com>",
        ),
        build(
            "Security alert: new sign-in on Windows",
            ["alice@example.com"],
            "We noticed a new sign-in to your account from Windows, Amsterdam.\nNot you? Reset your password.",
            "<div style='font-family:Segoe UI,Arial;border-left:4px solid #d13438;padding:8px 16px'>"
            "<h2 style='color:#d13438;margin:0'>New sign-in</h2>"
            "<p>Windows · Amsterdam, NL · 10:42</p>"
            "<p>Not you? <a href='https://example.com/security'>Secure your account</a></p></div>",
            bcc=["audit@example.com"],
            from_email="Account Security <security@example.com>",
        ),
        build(
            "Pull request #128 approved",
            ["bob@example.com"],
            "dave approved your pull request #128: Add MAILERS support.",
            "<p><b>dave</b> approved <a href='https://example.com/pr/128'>#128 Add MAILERS support</a></p>"
            "<blockquote style='border-left:3px solid #ccc;margin:0;padding-left:8px;color:#555'>"
            "LGTM, nice cleanup of the backend.</blockquote>",
            from_email="Code Review <reviews@example.com>",
        ),
        build(
            "Your subscription renews in 7 days",
            ["bob@example.com"],
            "Your Pony Pro plan renews on 3 November for EUR 9,00.",
            from_email="Billing <billing@example.com>",
        ),
        build(
            "Welcome to the team, Dave!",
            ["dave@example.org"],
            "Hi Dave,\n\nWelcome aboard! Your first week:\n- Mon: laptop + accounts\n- Tue: codebase tour\n- Wed: first ticket",
            "<h2>Welcome aboard, Dave! 🎉</h2><ol><li>Mon: laptop + accounts</li>"
            "<li>Tue: codebase tour</li><li>Wed: first ticket</li></ol>",
            cc=["team@example.com"],
            from_email="People Team <people@example.com>",
        ),
        build(
            "Votre réservation est confirmée",
            ["zoë@example.com"],
            "Table pour 2, samedi 20h00. Merci, Zoë !",
            "<p style='font-family:Georgia'>Table pour <b>2</b>, samedi <b>20h00</b>.</p><p>Merci, Zoë !</p>",
            from_email="Le Petit Poney <reservations@poney.example>",
        ),
        build(
            "[WARNING] Disk usage 91% on db-1",
            ["ops@example.com"],
            "Filesystem      Size  Used Avail Use% Mounted on\n/dev/sda1       200G  182G   18G  91% /var/lib/postgresql",
            from_email="monitoring@example.com",
        ),
        build(
            "Cron: nightly backup OK",
            ["ops@example.com"],
            "backup-2026-10-27.sql.gz  4.2 GB  uploaded in 3m12s",
            from_email="root@localhost",
        ),
        build(
            "Standup: blockers",
            ["team@example.com"],
            "Alice: waiting on API keys\nBob: none\nDave: onboarding",
            from_email="Standup Bot <standup@example.com>",
        ),
        build(
            "Internal: payroll run",
            ["finance@skip.example"],
            "POSTBOX_SKIP_DOMAINS contains skip.example: only forwarded, never captured.",
        ),
    ]


class Command(BaseCommand):
    help = "Send demo mails through the configured mail backend"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--bulk",
            type=int,
            default=0,
            help="Also send a mail to this many extra addresses, to fill the overview",
        )

    def handle(self, *args: Any, bulk: int, **options: Any) -> None:
        mails = demo_mails() + [
            build(
                f"Bulk mail {number}",
                [f"user{number:03d}@example.com"],
                f"Bulk mail number {number}.",
            )
            for number in range(1, bulk + 1)
        ]
        sent = sum(mail.send() for mail in mails)
        self.stdout.write(self.style.SUCCESS(f"Sent {sent} test mails"))
