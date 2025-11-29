from django.urls import path
from . import views

urlpatterns = [
    # path("video/events/", views.receiveLivekitEvents),
    path("<str:room_name>/messages/", views.get_room_messages),
    # path("<int:pk>/members/", views.RoomMembersView.as_view()),
    path("<str:room_name>/call/join/", views.join_livekit_room),
    path("<str:room_name>/call/start/", views.create_livekit_room),
]
