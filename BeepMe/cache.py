import redis.asyncio as async_redis
import os

class Cache: 
	def __init__(self):
		self.pool = async_redis.ConnectionPool.from_url(
			url = os.getenv("REDIS_URL"),
			decode_response = True,
		)
		self.redis = async_redis.Redis(connection_pool = self.pool)
		
	async def set(self, key, value, expire): 
		await self.redis.set(key, value, ex = expire)
		
	async def get(self, key):
		return await self.redis.get(key)
	
	async def cache_message(self, room_name, *messages):
		cached_messages_length = await self.redis.rpush(room_name, *messages)
		if cached_messages_length > 50: 
			await self.redis.ltrim(room_name, -50, -1)
	
	async def get_cached_messages(self, room_name):
		return await self.redis.lrange(room_name, 0, -1)
		
	async def set_user_online(self, user_id):
		#await self.redis.incrby(f"user_{user_id}_is_online")
		#await self.redis.expire(f"user_{user_id}_is_online", 30)
		await self.redis.sadd("online_users", user_id)
	
	async def remove_user_online(self, user_id):
		await self.redis.srem("online_users", user_id)
	
	async def is_user_online(self, *user_id):
		#await self.redis.exists(f"user_{user_id}_is_online")
		return await self.redis.sismember("online_users", *user_id)
		
	async def get_online_users(self, user_id_list):
		return self.redis.sinter("online_users", *user_id_list)
		
	async def add_active_member(self, user_id, room_name):
		await self.redis.sadd(f"{room_name}_online_members", user_id)
	
	async def get_active_members(self, room_name):
		return await self.redis.smembers(f"{room_name}_online_members")
		
	async def remove_active_member(self, user_id, room_name):
		await self.redis.srem(f"{room_name}_online_members", user_id)

	async def is_user_active_member(self, room_name, *user_id):
		return await self.redis.sismember(room_name, *user_id)
	
	async def get_online_inactive_members(self, room_name, user_ids):
		online_members_id = await self.is_user_online(*members_id)
		active_group_members_id = await self.is_user_active_member(room_name, *online_members_id)
		online_inactive_members_id = online_members_id - active_group_members_id
		return online_inactive_members_id
		
		
cache = Cache()