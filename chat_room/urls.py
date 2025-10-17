from django.urls import path
from . import views

urlpatterns = [
    # path("video/events/", views.receiveLivekitEvents),
    path("<str:room_name>/messages/", views.get_room_messages),
    # path("<int:pk>/members/", views.RoomMembersView.as_view()),
    path("<str:room_name>/video/auth/", views.get_livekit_JWT_token),
    path("<str:room_name>/", views.RoomDetailsView.as_view()),
]
