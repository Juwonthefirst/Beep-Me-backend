from rest_framework.pagination import CursorPagination
from rest_framework.pagination import Cursor


class ChatRoomPagination(CursorPagination):
    page_size = 20
    ordering = ["-last_message_time", "id"]


class MessagePagination(CursorPagination):
    page_size = 50
    ordering = ["-timestamp", "-id"]


def create_next_cursor(position: str, paginationInstance: MessagePagination):
    cursor = Cursor(offset=0, reverse=False, position=position)
    return paginationInstance.encode_cursor(cursor)
