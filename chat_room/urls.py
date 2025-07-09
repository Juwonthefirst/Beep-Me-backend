from django.urls import path
from . import views

urlpatterns = [
	path("<str:friend_username>/", views.GetChatRoomAndMessageByFriend.as_view()),
	path("<str:group_name>/", views.GetChatRoomAndMessageByGroup.as_view()),
	path("<int:pk>/messages/", views.get_room_messages),
	path("<int:pk>/members/", views.RoomMembersView.as_view()),
	path("<int:pk>/video/auth/", views.get_livekit_JWT_token),
]