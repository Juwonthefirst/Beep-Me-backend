from django.urls import path
from django.conf import settings
from . import views

urlpatterns = [
    path("attachment/url/", views.CreateUploadAttachmentURLView.as_view()),
    path("url/", views.GetUploadURLView.as_view()),
]

if settings.DEBUG:
    urlpatterns += [path("dev/<path:key>", views.DevelopmentUploadView.as_view())]
