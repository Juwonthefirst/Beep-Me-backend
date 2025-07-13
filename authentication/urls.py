from django.urls import path, include
from . import views
from user import views as user_views

urlpatterns = [
	path("login/", views.loginView),
	path("logout/", views.logoutView),
    path("social/google/ID/", views.google_login_by_id_token),
    path("social/google/code/", views.google_login_by_code_token),
	path("token/refresh/", views.CustomTokenRefreshView.as_view()),
	path("user/csrf/", views.get_csrf),
	path("user/rooms/", user_views.UserChatRoomsView.as_view()),
	path("user/notifications/", user_views.UserNotificationsView.as_view()),
	path("user/friends/", user_views.FriendListView.as_view()),
	path("user/friend-requests/sent/", user_views.SentFriendRequestView.as_view()),
	path("user/friend-requests/send/", user_views.sendFriendRequest),
	path("user/friend-requests/receive/", user_views.receivedFriendRequestView.as_view()),
	path("", include("djoser.urls")),
]