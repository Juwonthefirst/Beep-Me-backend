import asyncio
from functools import wraps
from asgiref.sync import async_to_sync
import os
from threading import Thread
from dotenv import load_dotenv


def load_enviroment_variables():
    load_dotenv()
    is_prod_enviroment = os.getenv("ENVIROMENT") == "production"
    if is_prod_enviroment:
        load_dotenv(".env.production", override=True)
        load_dotenv(".env.production.local", override=True)
    else:
        load_dotenv(".env.local", override=True)


load_enviroment_variables()

is_prod_enviroment = os.getenv("ENVIROMENT") == "production"


def cookify_response_tokens(tokens_to_cookify: dict[str, dict]):
    def wrapper(f):
        @wraps(f)
        def wrapped_function(*args, **kwargs):
            response = f(*args, **kwargs)
            if response.status_code == 200:
                for token_name in tokens_to_cookify:
                    token = response.data.pop(token_name, None)
                    token_config = tokens_to_cookify.get(token_name, {})
                    if not token:
                        continue

                    response.set_cookie(
                        key=token_name,
                        value=token,
                        secure=is_prod_enviroment,
                        httponly=True,
                        samesite="None" if is_prod_enviroment else "Lax",
                        **token_config,
                    )
            return response

        return wrapped_function

    return wrapper


# used for async functions
def async_background_task(f):
    @wraps(f)
    def wrapped_function(*args, **kwargs):
        try:
            loop = asyncio.get_running_loop()
            return loop.create_task(f(*args, **kwargs))
        except Exception as error:
            raise error

    return wrapped_function


# used for sync functions
def background_task(f):
    @wraps(f)
    def wrapped_function(*args, **kwargs):
        func = f
        if asyncio.iscoroutinefunction(f):
            func = async_to_sync(f)
        thread = Thread(target=func, args=[*args], kwargs={**kwargs}, daemon=True)
        thread.start()
        return thread

    return wrapped_function


def generate_chat_room_name(user_id: int | str, friend_id: int | str):

    room_name = f"chat-{user_id}-{friend_id}"
    if friend_id < user_id:
        room_name = f"chat-{friend_id}-{user_id}"

    return room_name
