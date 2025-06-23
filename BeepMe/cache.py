from redis.asyncio import Redis

class Cache: 
	def __init__(self):
		self.redis = Redis()
		
	async def set(self, key, value, expire): 
		await self.redis.set(key, value, ex = expire)
		
	async def get(self, key):
		return await self.redis.get(key).decode()
	
	async def cache_messages(self, key, messages, expire):
		await self.redis.hset(key, mapping = messages)
		await self.redis.expire(key, expire)
	
	async def add_cache_messages(self, key, messages):
		pass
	
	async def get_cached_messages(self, key):
		await self.redis.get(key).decode()
		
	async def set_user_online(self, user_id):
		await self.redis.incrby(f"user_{user_id}_is_online")
		await self.redis.expire(f"user_{user_id}_is_online", 30)
		
	async def is_user_online(self, user_id):
		await self.redis.exists(f"user_{user_id}_is_online")
		
	async def add_user_to_group(self, user, group):
		await self.redis.
		
	async def remove_user_from_group(self, arg):
		await
		
	async def user_in_group(self, user, group):
		await
	
	async def (self, arg):
		# Tab to edit	
		
cache = Cache()