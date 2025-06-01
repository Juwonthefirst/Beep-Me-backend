from django.urls import path
from . import views

urlpatterns = [
	path("<int:room_id>/", views.RoomDetailsView.as_view()),
	path("<int:room_id>/messages/", views.RoomMessagesView.as_view()),
	path("<int:room_id>/members/", views.RoomMembersView.as_view()),
]