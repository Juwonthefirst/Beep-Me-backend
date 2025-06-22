from django.urls import path
from . import views

urlpatterns = [
	path("profile-picture/", views.UploadProfilePicture.as_view()),
	path("profile-picture/<int:pk>/", views.getProfilePicture.as_view())
]