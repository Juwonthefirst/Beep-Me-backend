from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path("ws/chat/$", consumers.ChatConsumer.as_asgi()),
    re_path("ws/notification/$", consumers.NotificationConsumer.as_asgi()),
]