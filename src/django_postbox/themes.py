from __future__ import annotations

from typing import TYPE_CHECKING

from django_postbox.settings import settings

if TYPE_CHECKING:
    from django.http import HttpRequest

BUNDLED_THEMES = {
    "modern": "Modern",
    "mail2003": "Mail 2003",
    "mail2000": "Mail 2000",
    "mail2010": "Mail 2010",
}
COOKIE_NAME = "postbox_theme"


def available_themes() -> dict[str, str]:
    """Theme name -> label: the bundled ones plus a custom POSTBOX_THEME"""
    themes = dict(BUNDLED_THEMES)
    if settings.POSTBOX_THEME and settings.POSTBOX_THEME not in themes:
        themes[settings.POSTBOX_THEME] = settings.POSTBOX_THEME
    return themes


def get_theme(request: HttpRequest | None) -> str | None:
    """The viewer's theme cookie if it names a known theme, else POSTBOX_THEME"""
    chosen = request.COOKIES.get(COOKIE_NAME) if request else None
    # Only known names: the value ends up in a static file path
    return chosen if chosen in available_themes() else settings.POSTBOX_THEME
