---
title: Permissions
description: Decide who can open the inbox with DRF-style permission classes.
sidebar:
  order: 3
---

`POSTBOX_PERMISSIONS` is a list of classes or dotted paths. Every class must return `True` from `has_permission(request)`. Anonymous visitors are sent to `LOGIN_URL`, and logged-in users without access get a 403.

```python
POSTBOX_PERMISSIONS = ["django_postbox.permissions.IsStaff"]  # default
```

Included classes in `django_postbox.permissions`: `AllowAny`, `IsAuthenticated`, `IsStaff`, `IsSuperuser` and `DebugOnly`.

Write your own:

```python
from django_postbox.permissions import BasePermission


class IsQA(BasePermission):
    def has_permission(self, request):
        return request.user.groups.filter(name="QA").exists()
```

Captured mail often contains password reset links and tokens, so be careful with `AllowAny`.
