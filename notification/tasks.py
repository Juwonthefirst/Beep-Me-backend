from celery import shared_task
from channels.layer import get_channel_layer
from BeepMe.cache import cache

channel_layer = get_channel_layer()

@shared_task
async def send_notification(arg):
	await channel_layer.group_send(
		room_name, 
	)