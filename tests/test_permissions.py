import pytest
from django.contrib.auth.models import AnonymousUser, User
from django.test import RequestFactory

from django_postbox import permissions


@pytest.mark.parametrize(
    ("permission", "anonymous", "user", "staff", "superuser"),
    [
        (permissions.AllowAny, True, True, True, True),
        (permissions.IsAuthenticated, False, True, True, True),
        (permissions.IsStaff, False, False, True, True),
        (permissions.IsSuperuser, False, False, False, True),
    ],
)
def test_user_permissions(permission, anonymous, user, staff, superuser):
    request = RequestFactory().get("/")
    users = [
        AnonymousUser(),
        User(),
        User(is_staff=True),
        User(is_staff=True, is_superuser=True),
    ]
    results = []
    for request.user in users:
        results.append(permission().has_permission(request))
    assert results == [anonymous, user, staff, superuser]


def test_debug_only(settings):
    request = RequestFactory().get("/")
    settings.DEBUG = False
    assert not permissions.DebugOnly().has_permission(request)
    settings.DEBUG = True
    assert permissions.DebugOnly().has_permission(request)
