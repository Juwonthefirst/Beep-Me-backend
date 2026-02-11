from django.urls import path
from django.conf import settings
from . import views

urlpatterns = [
    path("attachment/", views.CreateAttachmentView.as_view()),
    path("attachment/<int:pk>/", views.DeleteAttachmentView.as_view()),
]

if settings.DEBUG:
    urlpatterns += [path("dev/<path:key>", views.DevelopmentUploadView.as_view())]
