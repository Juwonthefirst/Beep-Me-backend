from celery import shared_task
from channels.layers import get_channel_layer
from BeepMe.cache import cache
from asgiref.sync import async_to_sync
channel_layer = get_channel_layer()

@shared_task
def send_chat_notification(room, message, sender_id, sender_username):
	if room.is_group:
		members_id = room.group.members.values_list("id", flat = True)
	else:
		room_name = room.name
		members_id = room_name.split("_")[1:]
		
	online_inactive_members_id = async_to_sync(cache.get_online_inactive_members)(room.name, members_id) - {sender_id}
	for member_id in online_inactive_members_id:
		async_to_sync(channel_layer.group_send)(
			f"user_{member_id}_notifications", {"type": "notification.chat", "notification_detail": {
				"sender_id": sender_id,
				"sender": sender_username
				"receiver": room.group.name,
				"message": message,
				"is_group": room.is_group,
				"room_id": room.id
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
		
@shared_task
def send_call_notification(caller, room_object, video_call = False): 
	if room.is_group:
		members_id = room.group.members.values_list("id", flat = True)
	else:
		room_name = room.name
		members_id = room_name.split("_")[1:]
	
	online_members_id = async_to_sync(cache.online_members_id)(members_id) - {sender_id}
	for member_id in online_members_id:
	
		async_to_sync(channel_layer.group_send)(
			f"user_{member_id}_notifications", {"type": "notification.call", "notification_detail": {
				"caller": caller,
				"room_name": room.name,
				"is_video": video_call,
				"is_group": room.is_group,
				"room_id": room.id
				}
			}
		)