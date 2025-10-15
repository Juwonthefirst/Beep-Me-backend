from celery import shared_task
from BeepMe.cache import cache
from asgiref.sync import async_to_sync


@shared_task
def cache_messages(room_name, messages):
    async_to_sync(cache.cache_message)(room_name, *messages)
