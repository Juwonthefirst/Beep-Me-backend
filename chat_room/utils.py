import json

from rest_framework.pagination import Cursor

from BeepMe.storage import private_storage
from chat_room.pagination import MessagePagination


def create_next_cursor(position: str, paginationInstance: MessagePagination):
    cursor = Cursor(offset=0, reverse=False, position=position)
    return paginationInstance.encode_cursor(cursor)


def update_attachment_state(attachment: dict):
    attachment["url"] = private_storage.generate_file_url(attachment["path"])
    return attachment


def load_cached_chat_messages(messages: list[str]):
    unpacked_messages: list[dict[str, str]] = []

    for jsonified_message in messages:
        unpacked_message: dict = json.loads(jsonified_message)
        message_attachments: list[dict] = unpacked_message["attachments"]
        unpacked_message["attachments"] = [
            update_attachment_state(attachment) for attachment in message_attachments
        ]
        unpacked_messages.append(unpacked_message)

    return unpacked_messages
