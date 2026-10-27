"""DRF style permission classes for the postbox views, set via POSTBOX_PERMISSIONS"""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.conf import settings

if TYPE_CHECKING:
    from django.http import HttpRequest


class BasePermission:
    def has_permission(self, request: HttpRequest) -> bool:
        return True


class AllowAny(BasePermission):
    pass


class IsAuthenticated(BasePermission):
    def has_permission(self, request: HttpRequest) -> bool:
        return request.user.is_authenticated


class IsStaff(BasePermission):
    def has_permission(self, request: HttpRequest) -> bool:
        return getattr(request.user, "is_staff", False) and request.user.is_active


class IsSuperuser(BasePermission):
    def has_permission(self, request: HttpRequest) -> bool:
        return getattr(request.user, "is_superuser", False) and request.user.is_active


class DebugOnly(BasePermission):
    def has_permission(self, request: HttpRequest) -> bool:
        return settings.DEBUG
