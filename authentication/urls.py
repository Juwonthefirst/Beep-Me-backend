from django.urls import path, include
from . import views
from user import views as user_views

urlpatterns = [
    path("login/", views.loginView),
    path("logout/", views.logoutView),
    path("social/google/ID/", views.google_login_by_id_token),
    path("social/google/code/", views.google_login_by_code_token),
    path("token/refresh/", views.CustomTokenRefreshView.as_view()),
    path("user/rooms/", user_views.UserChatRoomsView.as_view()),
    path("user/rooms/<str:name>/", user_views.RetrieveUserChatRoomView.as_view()),
    path("user/notifications/", user_views.UserNotificationsView.as_view()),
    path("user/friends/", user_views.FriendListView.as_view()),
    path("user/friend-requests/sent/", user_views.SentFriendRequestView.as_view()),
    path("user/friend-requests/send/", user_views.sendFriendRequest),
    path(
        "user/friend-requests/receive/", user_views.receivedFriendRequestView.as_view()
    ),
    path("user/update/username/", user_views.update_username),
    path("", include("djoser.urls")),
]
