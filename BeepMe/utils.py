import asyncio
from functools import wraps
from asgiref.sync import async_to_sync
import os
from threading import Thread

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
                        max_age=token_config.pop("max_age", 60 * 60 * 60 * 24),
                        **token_config,
                    )
            return response

        return wrapped_function

    return wrapper


def async_background_task(f):
    @wraps(f)
    def wrapped_function(*args, **kwargs):
        return asyncio.create_task(f(*args, **kwargs))

    return wrapped_function


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
