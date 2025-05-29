from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from urllib.parse import parse_qs


class JWTAuthMiddleware(BaseMiddleware):
	async def __call__(self, scope, recieve, send):
		query_string = scope["query_string"].decode()
		token = parse_qs(query_string).get("token", [None])[0]
		scope["user"] = None
		
		if token:
			try:
				validated_token = AccessToken(token)
				user = await database_sync_to_async(get_user_model().objects.get)(id = validated_token["user_id"])
				scope["user"] = user
			except:
				scope["user"] = None
		
		return await super().__call__(scope, recieave, send)