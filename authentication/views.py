from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from secrets import token_hex
from google.oauth2 import id_token
from google.auth.transport import requests
from allauth.account.models import EmailAddress
from authlib.integrations.requests_client import OAuth2Session

User = get_user_model()
bad_request = status.HTTP_400_BAD_REQUEST
client = OAuth2Session(google_client_id, google_client_secret, redirect_uri = "postmessage")
google_client_id = os.getenv("GOOGLE_CLIENT_ID")
google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

def verify_id_token(token):
	try:
		return id_token.verify_oauth2_token(token, requests.Request())
	except:
		return None

@api_view(["POST"])		
def googleLoginByIdToken(request):
	id_token = request.data.get("token")
	if not id_token: 
		return Response({"error": "token is required"}, status = bad_request)
			
	data = verify_id_token(id_token)	
	if not data: 
		return Response({"error": "Invalid token"}, status = bad_request)
			
	email = data.get("email")
	if not email:
		return Response({"error": "Unable to get email"}, status = bad_request)
				
	try: 
		user = User.objects.get(email = email)
		if not user.is_active: 
			raise User.DoesNotExist
		new_user = False
	except User.DoesNotExist:
		user = User.objects.create_user(
			username = email.rstrip("@gmail.com") + str(token_hex(8)), 
			email = email, 
			password = f'pass_{token_hex(32)}',
			first_name = first_name,
			last_name = last_name
		)
		
		EmailAddress.objects.create(
			user = user,
			email = email,
			primary = True,
			verified = True
		)
		new_user = True
				
	refresh_token = RefreshToken.for_user(user)
			
	response = Response({
		"access": str(refresh_token.access_token),
		"user" : {
			"id": user.id,
			"username": user.username,
			"email": user.email,
			"firstname": user.first_name,
			"lastname": user.last_name
		},
		"new_user": new_user
	})
	
	response.set_cookie(
		key = "refresh_token",
		value = str(refresh_token),
		secure = True,
		httponly = True,
		max_age = 60 * 60 * 24 * 30,
		samesite = 'None'
	)
	
	return response

@api_view(["POST"])	
def googleLoginByCode(request): 
	code = request.data.get("code")
	if not code: 
		return Response({"error": "No code provided"}, status = bad_request)
		
	token = client.fetch_token("https://oauth2.googleapis.com/token", code = code)
	id_token = token.get("id_token")
	id_info = client.parse_id_token(id_token)
	email = id_info.get("email")
	first_name = id_info.get("given_name")
	last_name = id_info.get("family_name")
	
	if not email:
		return Response({"error": "Unable to get email"}, status = bad_request)
				
	try: 
		user = User.objects.get(email = email)
		if not user.is_active: 
			raise User.DoesNotExist
		new_user = False
	except User.DoesNotExist:
		user = User.objects.create_user(
			username = email.rstrip("@gmail.com") + str(token_hex(8)), 
			email = email, 
			password = f'pass_{token_hex(32)}',
			first_name = first_name,
			last_name = last_name
		)
		
		EmailAddress.objects.create(
			user = user,
			email = email,
			primary = True,
			verified = True
		)
		new_user = True
				
	refresh_token = RefreshToken.for_user(user)
	response = Response({
		"access": str(refresh_token.access_token),
		"user" : {
			"id": user.id,
			"username": user.username,
			"email": user.email,
			"firstname": user.first_name,
			"lastname": user.last_name
		},
		"new_user": new_user
	})
	
	response.set_cookie(
		key = "refresh_token",
		value = str(refresh_token),
		secure = True,
		httponly = True,
		max_age = 60 * 60 * 24 * 30,
		samesite = 'None'
	)
	
	return response