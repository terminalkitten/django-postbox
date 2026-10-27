from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

from django.conf import settings as django_settings

if TYPE_CHECKING:
    from collections.abc import Sequence

__all__ = ["settings"]

T = TypeVar("T")


class Setting(Generic[T]):
    """A Django setting with a default, read each time it is accessed"""

    def __init__(self, default: T) -> None:
        self.default = default
        self.name = ""

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name

    def __get__(self, instance: object, owner: type | None = None) -> T:
        return getattr(django_settings, self.name, self.default)


class PostboxSettings:
    POSTBOX_FORWARD_BACKEND: Setting[str | None] = Setting(None)
    POSTBOX_STORAGE: Setting[str] = Setting("django_postbox.storages.DatabaseStorage")
    POSTBOX_CACHE: Setting[str] = Setting("default")
    POSTBOX_SKIP_DOMAINS: Setting[Sequence[str]] = Setting(())
    POSTBOX_PERMISSIONS: Setting[Sequence[type | str]] = Setting(
        ("django_postbox.permissions.IsStaff",)
    )
    POSTBOX_LOAD_HTMX: Setting[bool] = Setting(True)
    POSTBOX_THEME: Setting[str | None] = Setting("modern")


settings = PostboxSettings()
