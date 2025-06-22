from django.urls import path
from . import views


urlpatterns = [
	path("", views.UsersView.as_view()),
	path("<int:pk>/", views.RetrieveUserView.as_view()),
	path("rooms/", views.GetUserChatRooms.as_view()),
	path("notifications/", views.GetUserNotifications.as_view())
	
]