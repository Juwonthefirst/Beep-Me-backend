from rest_framework.pagination import CursorPagination


class ChatRoomPagination(CursorPagination):
    page_size = 20
    ordering = ["-last_room_activity", "id"]


class MessagePagination(CursorPagination):
    page_size = 50
    ordering = ["-created_at", "-id"]
