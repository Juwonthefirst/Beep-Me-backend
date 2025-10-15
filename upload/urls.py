from django.urls import path
from . import views

urlpatterns = [
    path("profile-picture/", views.UploadProfilePictureView.as_view()),
    path("profile-picture/<int:user_id>/", views.GetProfilePictureView.as_view()),
    path("profile-picture/group/<int:group_id>/", views.GetGroupPictureView.as_view()),
    path("attachment/<int:message_id>/", views.GetAttachmentFileView.as_view()),
]
