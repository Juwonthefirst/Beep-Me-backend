from django.urls import path
from . import views


urlpatterns = [
	path("", views.UsersView.as_view()),
	path("<int:pk>/", views.RetrieveUserView.as_view()),
	path("exists/", views.DoesUsernameExistView.as_view()),
	path("rooms/", views.UserChatRoomsView.as_view()),
	path("notifications/", views.UserNotificationsView.as_view())
	
]