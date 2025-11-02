import asyncio
from functools import wraps
from asgiref.sync import async_to_sync
import os
from threading import Thread

is_prod_enviroment = os.getenv("ENVIROMENT") == "production"


def cookify_response_tokens(f):
    @wraps(f)
    def wrapped_function(*args, **kwargs):
        response = f(*args, **kwargs)
        if (
            "access" in response.data
            and "refresh" in response.data
            and response.status_code == 200
        ):
            new_access_token = response.data.pop("access")
            new_refresh_token = response.data.pop("refresh")
            response.set_cookie(
                key="access_token",
                value=new_access_token,
                secure=is_prod_enviroment,
                httponly=True,
                max_age=60 * 60,
                samesite="None",
            )

            response.set_cookie(
                key="refresh_token",
                value=new_refresh_token,
                secure=is_prod_enviroment,
                httponly=True,
                max_age=60 * 60 * 24 * 30,
                samesite="None",
            )

        return response

    return wrapped_function


def async_background_task(f):
    @wraps(f)
    def wrapped_function(*args, **kwargs):
        return asyncio.create_task(f(*args, **kwargs))

    return wrapped_function


def background_task(f):
    @wraps(f)
    def wrapped_function(*args, **kwargs):
        if asyncio.iscoroutinefunction(f):
            f = async_to_sync(f)
        Thread(target=f, args=[*args], kwargs={**kwargs}, daemon=True)

    return wrapped_function
