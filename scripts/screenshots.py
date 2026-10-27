"""
Render the README and docs screenshots with headless Chrome, and export the logo.

Uses a throwaway in-memory database filled with the demo mails, so your own
db/postbox.db is never touched. Set CHROME to the browser binary if it is not found.

    uv run python scripts/screenshots.py
"""

from __future__ import annotations

import os
import random
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATIC = ROOT / "src/django_postbox/static"
IMAGES = ROOT / "docs/img"
PUBLIC = ROOT / "public"
CHROME_CANDIDATES = (
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "google-chrome",
    "chromium",
    "chromium-browser",
)
WINDOW = "1280,760"


def find_chrome() -> str:
    for candidate in (os.environ.get("CHROME"), *CHROME_CANDIDATES):
        if candidate and (
            path := shutil.which(candidate) or (Path(candidate).is_file() and candidate)
        ):
            return path
    sys.exit("Chrome not found, set CHROME=/path/to/chrome")


def setup_django() -> None:
    sys.path.insert(0, str(ROOT))
    os.environ["DJANGO_SETTINGS_MODULE"] = "tests.project.settings"
    import django
    from django.conf import settings
    from django.core.management import call_command

    # Before setup, so no connection to db/postbox.db is ever made
    settings.DATABASES["default"]["NAME"] = ":memory:"
    settings.POSTBOX_FORWARD_BACKEND = None
    django.setup()
    call_command("migrate", verbosity=0)


def render_pages() -> dict[str, str]:
    """name -> page HTML, with static URLs pointing at the files on disk"""
    from django.contrib.auth.models import User
    from django.test import Client, override_settings

    from django_postbox.backends import EmailBackend
    from django_postbox.storages import get_storage, hash_address
    from tests.project.management.commands.send_test_mails import (
        demo_mails,
        random_mails,
    )

    # Random people first (fixed seed for stable images), so the real ones are on top
    EmailBackend().send_messages(random_mails(10, random.Random(42)) + demo_mails())

    client = Client()
    client.force_login(User.objects.create(username="docs", is_staff=True))
    alice = hash_address("alice@example.com")
    by_subject = {message.subject: message for message in get_storage().messages(alice)}
    newsletter = by_subject["The Weekly Pony #42"]
    order = by_subject["Your order #10042 has shipped"]

    pages = {
        "overview": "/dev/inbox/",
        "inbox": f"/dev/inbox/{alice}/{newsletter.id}/",
        "order": f"/dev/inbox/{alice}/{order.id}/",
        "search": f"/dev/inbox/{alice}/?q=re&tab=text",
    }
    html = {}
    for theme in ("mail2000", "mail2003"):
        with override_settings(POSTBOX_THEME=theme):
            for name, url in pages.items():
                content = client.get(url).content.decode()
                html[f"{name}-{theme}"] = content.replace(
                    "/static/", f"{STATIC.as_uri()}/"
                )
    return html


def screenshot(chrome: str, html: str, target: Path, workdir: Path) -> None:
    page = workdir / f"{target.stem}.html"
    page.write_text(html)
    subprocess.run(
        [
            chrome,
            "--headless=new",
            "--disable-gpu",
            "--hide-scrollbars",
            "--force-device-scale-factor=2",
            f"--window-size={WINDOW}",
            f"--screenshot={target}",
            page.as_uri(),
        ],
        check=True,
        capture_output=True,
    )


def main() -> None:
    chrome = find_chrome()
    setup_django()
    IMAGES.mkdir(parents=True, exist_ok=True)
    PUBLIC.mkdir(exist_ok=True)

    logo = STATIC / "postbox/logo.svg"
    for target in (IMAGES / "logo.svg", PUBLIC / "logo.svg", PUBLIC / "favicon.svg"):
        shutil.copyfile(logo, target)

    with tempfile.TemporaryDirectory() as workdir:
        for name, html in render_pages().items():
            target = IMAGES / f"{name}.png"
            screenshot(chrome, html, target, Path(workdir))
            print(f"{target.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
