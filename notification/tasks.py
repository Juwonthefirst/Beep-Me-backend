from celery import shared_task
from channels.layer import get_channel_layer
from BeepMe.cache import cache

channel_layer = get_channel_layer()

@shared_task
async def send_chat_notification(room, message, sender_id):

	if room.is_group:
		members_id = room.group.members.related_name("id")
		online_members_id = await cache.is_user_online(room.name, *members_id)
		active_group_members_id = await cache.is_user_active_member(room.name, *online_members_id)
		online_inactive_members_id = await cache.sdiff(online_members_id, active_group_members_id, sender_id)
		
		for member_id in online_inactive_members_id:
			
			await channel_layer.group_send(
				f"user_{member_id}_notifications", {"type": "notification.chat", "notification_detail": {
					"sender": sender_id,
					"receiver": room.group.name,
					"message": message,
					"is_group": True
					}
				}
			)
	else:
		room_name = room.name
		receiver = room_name.split("_")
		receiver.remove(sender_id)
		if (
			not await cache.is_user_online(receiver) or 
			await cache.is_user_active_member(room_name, receiver)
		): 
			return 
		
		await channel_layer.group_send(
			room_name, {"type": "notification.chat", "notification_detail": {
				"sender": sender_id,
				"receiver": receiver,
				"message": message,
				"is_group": room.is_group
				}
			}
		)
	
@shared_task
async def send_group_notification(): 
	pass