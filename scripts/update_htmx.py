"""Download the latest htmx release into the postbox static folder"""

from __future__ import annotations

import json
import urllib.request
from pathlib import Path

REGISTRY_URL = "https://registry.npmjs.org/htmx.org/latest"
DOWNLOAD_URL = "https://unpkg.com/htmx.org@{version}/dist/htmx.min.js"
TARGET = Path(__file__).parent.parent / "src/django_postbox/static/postbox/htmx.min.js"


def main() -> None:
    with urllib.request.urlopen(REGISTRY_URL, timeout=30) as response:
        version = json.load(response)["version"]
    with urllib.request.urlopen(
        DOWNLOAD_URL.format(version=version), timeout=30
    ) as response:
        source = response.read().decode()
    TARGET.write_text(f"/* htmx {version} */\n{source}")
    print(f"htmx {version} -> {TARGET}")


if __name__ == "__main__":
    main()
