from django.urls import path
from . import views

urlpatterns = [
	path("<int:room_id>/messages/", views.RoomMessagesView.as_view())
]