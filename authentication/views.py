from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from secrets import token_hex
from asgiref.sync import sync_to_async
from google.oauth2 import id_token
from google.auth.transport import requests

User = get_user_model()
bad_request = status.HTTP_400_BAD_REQUEST

@sync_to_async
def verify_id_token(token):
	try:
		return id_token.verify_oauth2_token(token, requests.Request())
	except:
		return None

class GoogleLoginView(APIView):
	async def post(self, request):
		id_token = await request.data.get("token")
		if not id_token: 
			return Response({"error": "token is required"}, status = bad_request)
			
		data = await verify_id_token(id_token)	
		if not data: 
			return Response({"error": "Invalid token"}, status = bad_request)
			
		email = data.get("email")
		if not email:
			return Response({"error": "Unable to get email"}, status = bad_request)
				
		try: 
			user = await database_sync_to_async(User.objects.get)(email = email)
			new_user = False
		except User.DoesNotExist:
			user = await database_sync_to_async(User.objects.create_user)(username = email.replace('@', "_"), email = email, password = f'pass_{token_hex(32)}')
			new_user = True
				
		refresh_token = RefreshToken.for_user(user)
			
		return Response({
			"refresh": str(refresh_token),
			"access": str(refresh_token.access_token),
			"user": {
				"id": user.id,
				"username": user.username,
				"email": user.email,
			},
			"new_user": new_user
		})
		