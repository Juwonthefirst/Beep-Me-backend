import redis.asyncio as async_redis
import os
from .utils import load_enviroment_variables

load_enviroment_variables()


class Cache:
    def __init__(self):
        pool = async_redis.ConnectionPool.from_url(
            url=os.getenv("REDIS_URL"), decode_responses=True
        )
        self.redis = async_redis.Redis(connection_pool=pool)

    async def set(self, key, value, expiry_time=60):
        await self.redis.set(key, value, ex=expiry_time)

    async def set_hash(self, key, mapping, expiry_time):
        await self.redis.hset(key, mapping=mapping)
        if expiry_time:
            await self.redis.expire(key, expiry_time)

    async def set_hash_field(self, hash_key, field_key, value):
        await self.redis.hset(hash_key, field_key, value)

    async def delete_hash_field(self, hash_key, field_key):
        await self.redis.hdel(hash_key, field_key)

    async def increase_hash_field(self, hash_key, field_key, amount=1):
        await self.redis.hincrby(hash_key, field_key, amount)

    async def get_hash_field(self, hash_key, field_key):
        return await self.redis.hget(hash_key, field_key)

    async def get_hash(self, hash_key):
        return await self.redis.hgetall(hash_key)

    async def get(self, key):
        return await self.redis.get(key)

    async def delete(self, key):
        await self.redis.delete(key)

    async def set_expire_time(self, key: str, amount: int):
        await self.redis.expire(key, amount)

    async def ping(self, user_id):
        await self.redis.set(f"user_{user_id}_is_online", 1, ex=50)

    async def cache_message(self, room_name: str, messages: list[str] | str):
        try:
            if isinstance(messages, str):
                messages = [messages]

            cached_messages_length = await self.redis.lpush(
                f"{room_name}_messages", *messages
            )
            if cached_messages_length > 50:
                await self.redis.rtrim(f"{room_name}_messages", -50, -1)
        except Exception as error:
            print(error)

    async def get_cached_messages(self, room_name):
        return await self.redis.lrange(f"{room_name}_messages", 0, -1)

    async def add_user_online(self, user_id):
        await self.redis.sadd("online_users", user_id)

    async def remove_user_online(self, user_id):
        await self.redis.delete(f"user_{user_id}_is_online")
        await self.redis.srem("online_users", user_id)

    async def is_user_online(self, user_id: int):
        return await self.redis.sismember("online_users", user_id)

    async def get_online_users(self, user_id_list: list[int]):
        are_users_online = await self.redis.smismember("online_users", user_id_list)
        return {
            user_id
            for index, user_id in enumerate(user_id_list)
            if are_users_online[index]
        }

    async def add_active_member(self, room_name: str, user_id: int):
        await self.redis.sadd(f"{room_name}_online_members", user_id)

    async def get_active_members(self, room_name):
        return await self.redis.smembers(f"{room_name}_online_members")

    async def remove_active_member(self, user_id, room_name):
        await self.redis.srem(f"{room_name}_online_members", user_id)

    async def is_user_active_member(self, room_name, users_id):
        are_users_online = await self.redis.smismember(
            f"{room_name}_online_members", users_id
        )
        return {
            user_id for index, user_id in enumerate(users_id) if are_users_online[index]
        }

    async def get_online_inactive_members(self, room_name, members_id):
        online_members_id = await self.get_online_users(members_id)
        active_group_members_id = await self.is_user_active_member(
            room_name, online_members_id
        )
        online_inactive_members_id = online_members_id - active_group_members_id
        return online_inactive_members_id


cache = Cache()
