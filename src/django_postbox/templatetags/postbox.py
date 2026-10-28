from datetime import datetime, timedelta

from django import template
from django.template import Context
from django.templatetags.static import static
from django.utils import timezone
from django.utils.html import format_html, format_html_join
from django.utils.safestring import SafeString
from django.utils.timesince import timesince

from django_postbox.settings import settings
from django_postbox.themes import get_theme

register = template.Library()


@register.simple_tag(takes_context=True)
def postbox_assets(context: Context) -> SafeString:
    """
    The base stylesheet, the theme stylesheet (the viewer's cookie, else
    POSTBOX_THEME) and, unless POSTBOX_LOAD_HTMX is off, the bundled htmx.
    Rendered server side in <head>, so a chosen theme never flickers.
    """
    stylesheets = ["postbox/postbox.css"]
    if theme := get_theme(context.get("request")):
        stylesheets.append(f"postbox/themes/{theme}.css")
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
    """Return "just now" within a minute, else the largest unit: "3 hours ago"."""
    if timezone.now() - moment < timedelta(minutes=1):
        return "just now"
    return f"{timesince(moment, depth=1)} ago"
