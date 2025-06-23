import redis.asyncio as async_redis

class Cache: 
	def __init__(self):
		self.pool = async_redis.ConnectionPool.from_url(
			url = os.getenv("REDIS_URL"),
			decode_response = True,
			ssl = True
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
	
	async def get_cached_messages(self, key):
		return await self.redis.lrange(key, 0, -1)
		
	async def set_user_online(self, user_id):
		await self.redis.incrby(f"user_{user_id}_is_online")
		await self.redis.expire(f"user_{user_id}_is_online", 30)
		
	async def is_user_online(self, user_id):
		await self.redis.exists(f"user_{user_id}_is_online")
		
	async def add_active_members(self, user_id, room_name):
		await self.redis.sadd(f"{room_name}_online_members", user_id)
	
	async def get_active_members(self, room_name):
		return await self.redis.smembers(f"{room_name}_online_members")
		
	async def remove_from_group(self, arg):
		await
		
	async def user_in_group(self, user, group):
		await
	
	async def (self, arg):
		# Tab to edit	
		
cache = Cache()