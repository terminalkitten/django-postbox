---
title: Who can read the inbox
description: Keep captured mail behind the right login, from staff only to a QA group or an open review server.
sidebar:
  order: 2
---

Captured mail is sensitive: it holds password reset links, invite tokens and personal data. So by default only **staff users** can open the inbox. Visitors who are not logged in go to your login page, and logged in users without access get a "403 Forbidden".

You decide who gets in with `POSTBOX_PERMISSIONS`: a list of permission classes, in the style of Django REST framework. Every class must say yes.

## Staff only (the default)

Nothing to configure. This is the same as:

```python title="settings.py"
POSTBOX_PERMISSIONS = ["django_postbox.permissions.IsStaff"]
```

## Your QA team

Write a class with a `has_permission(request)` method and point the setting at it:

```python title="myproject/permissions.py"
from django_postbox.permissions import BasePermission


class IsQA(BasePermission):
    """Members of the "QA" group may read captured mail"""

    def has_permission(self, request):
        return request.user.groups.filter(name="QA").exists()
```

```python title="settings.py"
POSTBOX_PERMISSIONS = ["myproject.permissions.IsQA"]
```

## Everyone, but only while debugging

On a local machine or a throwaway review app you may not want a login at all. Combine the built-in classes:

```python title="settings.py"
POSTBOX_PERMISSIONS = ["django_postbox.permissions.DebugOnly"]
```

`DebugOnly` lets everyone in while `DEBUG = True`, and nobody once it is off. That makes a forgotten URL on a production server harmless.

:::caution
`AllowAny` really means anyone who can reach the URL. Only use it on a machine that is not reachable from the internet.
:::

## Built-in classes

| Class | Lets in |
| --- | --- |
| `IsStaff` | Active staff users (default) |
| `IsSuperuser` | Active superusers |
| `IsAuthenticated` | Any logged in user |
| `DebugOnly` | Everyone, while `DEBUG = True` |
| `AllowAny` | Everyone |

All of them live in `django_postbox.permissions`. You can list classes or their dotted paths, and mix your own with the built-in ones.
