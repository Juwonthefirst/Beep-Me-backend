from celery import shared_task
from channels.layer import get_channel_layer
from BeepMe.cache import cache
from asigref.sync import async_to_sync
channel_layer = get_channel_layer()

@shared_task
def send_chat_notification(room, message, sender_id):
	
	if room.is_group:
		members_id = room.group.members.values_list("id", flat = True)
		online_inactive_members_id = async_to_sync(cache.get_online_inactive_members)(room.name, members_id) - {sender_id}
		for member_id in online_inactive_members_id:
			
			async_to_sync(channel_layer.group_send)(
				f"user_{member_id}_notifications", {"type": "notification.chat", "notification_detail": {
					"sender": sender_id,
					"receiver": room.group.name,
					"message": message,
					"is_group": True,
					"room_id": room.id
					}
				}
			)
			
	else:
		room_name = room.name
		members_id = room_name.split("_")[1:]
		online_inactive_members_id = async_to_sync(cache.get_online_inactive_members)(room.name, members_id) - {sender_id}
		async_to_sync(channel_layer.group_send)(
			f"user_{member_id}_notifications", {"type": "notification.chat", "notification_detail": {
				"sender": sender_id,
				"receiver": receiver,
				"message": message,
				"is_group": room.is_group
				}
			}
		)
	
@shared_task
def send_group_notification(room, notification, sender_id): 
	members_id = room.group.members.values_list("id", flat = True)
	online_inactive_members_id = async_to_sync(cache.get_online_inactive_members)(room.name, members_id) - {sender_id}
	for member_id in online_inactive_members_id:
			
		async_to_sync(channel_layer.group_send)(
			f"user_{member_id}_notifications", {
				"type": "notification.group", "notification_detail": {
				"group_id": group_id,
				"notification": notification
				}
			}
		)
		
@shared_task
def send_online_status_notification(user, status): 
	friends_id = user.get_friends().values_list("id", flat = True)
	online_friends_id = async_to_sync(cache.is_user_online)(*friends_id)
	
	for friend_id in online_friends_id:
		async_to_sync(channel_layer.group_send)(
			f"user_{friend_id}_notifications", {
				"type": "notification.online", "notification_detail": {
				"user": user,
				"status": status,
				"notification": notification
			}
		})
		
@shared_task
def send_friend_request_notification(user_id, friend_id, action):
	if async_to_sync(cache.is_user_online)(friend_id): 
		async_to_sync(channel_layer.group_send)(
			f"user_{friend_id}_notifications", {"type": "notification.friend", "notification_detail": {
				"sender": user_id,
				"receiver": receiver_id,
				"action": action,
				}
			}
		)