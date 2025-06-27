from django.urls import path
from . import views

urlpatterns = [
	path("<int:pk>/", views.RoomDetailsView.as_view()),
	path("<int:pk>/messages/", views.get_room_messages),
	path("<int:pk>/members/", views.RoomMembersView.as_view()),
]