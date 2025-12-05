from django.urls import path
from . import views

urlpatterns = [
    path("attachment/url/", views.CreateUploadAttachmentURLView.as_view()),
]
