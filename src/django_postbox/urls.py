from django.urls import path

from django_postbox import views

app_name = "postbox"

urlpatterns = [
    path("", views.OverviewView.as_view(), name="overview"),
    path("clear/", views.ClearView.as_view(), name="clear_all"),
    path("settings/", views.SettingsView.as_view(), name="settings"),
    path("<str:hash>/", views.InboxView.as_view(), name="inbox"),
    path("<str:hash>/clear/", views.ClearView.as_view(), name="clear"),
    path("<str:hash>/<uuid:pk>/", views.MessageView.as_view(), name="message"),
    path(
        "<str:hash>/<uuid:pk>/raw/",
        views.MessageRawView.as_view(),
        name="message_raw",
    ),
    path(
        "<str:hash>/<uuid:pk>/attachments/<int:index>/",
        views.AttachmentView.as_view(),
        name="attachment",
    ),
    path(
        "<str:hash>/<uuid:pk>/delete/",
        views.DeleteMessageView.as_view(),
        name="delete",
    ),
]
