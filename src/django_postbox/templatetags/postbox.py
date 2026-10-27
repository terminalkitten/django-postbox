from datetime import datetime, timedelta

from django import template
from django.templatetags.static import static
from django.utils import timezone
from django.utils.html import format_html, format_html_join
from django.utils.safestring import SafeString
from django.utils.timesince import timesince

from django_postbox.settings import settings

register = template.Library()


@register.simple_tag
def postbox_assets() -> SafeString:
    """
    The base stylesheet, the POSTBOX_THEME stylesheet and, unless
    POSTBOX_LOAD_HTMX is off, the bundled htmx
    """
    stylesheets = ["postbox/postbox.css"]
    if settings.POSTBOX_THEME:
        stylesheets.append(f"postbox/themes/{settings.POSTBOX_THEME}.css")
    links = format_html_join(
        "",
        '<link rel="stylesheet" href="{}">',
        ((static(path),) for path in stylesheets),
    )
    if not settings.POSTBOX_LOAD_HTMX:
        return links
    return format_html(
        '{}<script src="{}" defer></script>', links, static("postbox/htmx.min.js")
    )


@register.filter
def ago(moment: datetime) -> str:
    """Return "just now" within a minute, else "<timesince> ago"."""
    if timezone.now() - moment < timedelta(minutes=1):
        return "just now"
    return f"{timesince(moment)} ago"
