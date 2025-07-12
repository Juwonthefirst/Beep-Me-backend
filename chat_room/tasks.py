from celery import shared_task
from BeepMe.cache import cache

@shared_task
def cache_messages(messages): 
	async_to_sync(cache.cache_message)(room.name, *messages)