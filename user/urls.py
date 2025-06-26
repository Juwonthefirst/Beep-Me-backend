from django.urls import path
from . import views


urlpatterns = [
	path("", views.UsersView.as_view()),
	path("<int:pk>/", views.RetrieveUserView.as_view()),
	path("exists/", views.DoesUsernameExistView.as_view()),
	path("rooms/", views.UserChatRoomsView.as_view()),
	path("notifications/", views.UserNotificationsView.as_view()),
	path("friends/", views.FriendListView.as_view()),
	path("friend-requests/send/", views.SentFriendRequestView.as_view()),
	path("friend-requests/send/", views.sendFriendRequest),
	path("friend-requests/receive/", views.receivedFriendRequestView.as_view()),

	
]