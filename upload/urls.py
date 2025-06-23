from django.urls import path
from . import views

urlpatterns = [
	path("profile-picture/", views.UploadProfilePicture.as_view()),
	path("profile-picture/<int:user_id>/", views.GetProfilePicture.as_view()),
	path("attachment/<int:message_id>/", views.GetAttachmentFile.as_view()),
	
]