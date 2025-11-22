from rest_framework.pagination import CursorPagination


class ChatRoomPagination(CursorPagination):
    page_size = 20
    ordering = ["-last_message_time", "-id"]


class MessagePagination(CursorPagination):
    page_size = 50
    ordering = ["-timestamp", "-id"]
