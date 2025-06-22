from redis.asyncio import Redis

class Cache: 
	def __init__(self):
		self.redis = Redis()
		
	async def set(self, key, value, expire): 
		await redis.set(key, value, ex = expire)
		
	async def get(self, key):
		return await redis.get(key).decode()
	
	async def cache_messages(self, key, messages, expire):
		await redis.hset(key, mapping = messages)
		await redis.expire(key, expire)
	
	async def add_cache_messages(self, key, messages):
		pass
	
	async def get_cached_messages(self, key):
		await redis.get(key).decode()
		
	async def set_user_online(self, user_id):
		await redis.set(f"user_{user_id}_is_online", 1)
		
	async def (self, arg):
		# Tab to edit