from BeepMe.cache import cache
from BeepMe.utils import background_task


@background_task
async def cache_messages(room_name, messages):
    await cache.cache_message(room_name, *messages)
