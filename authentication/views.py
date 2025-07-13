from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django.utils.datastructures import MultiValueDict
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from django.db.models import Q
from secrets import token_hex
from google.oauth2 import id_token
from google.auth.transport import requests
from authlib.integrations.requests_client import OAuth2Session
from authentication.serializers import LoginSerializer
import os


User = get_user_model()
bad_request = status.HTTP_400_BAD_REQUEST
unauthorized = status.HTTP_401_UNAUTHORIZED
forbidden = status.HTTP_403_FORBIDDEN
google_client_id = os.getenv("GOOGLE_CLIENT_ID")
google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
client = OAuth2Session(google_client_id, google_client_secret, redirect_uri = "postmessage")

@api_view(["GET"])
@ensure_csrf_cookie
def get_csrf(request):
	csrf_token = request.COOKIES.get("csrftoken")
	if csrf_token: 
		return Response({"csrf_token": csrf_token})
	
	return Response({"error": "no csrf token found"}, status = bad_request)
	
	
def verify_id_token(token):
	try:
		return id_token.verify_oauth2_token(token, requests.Request())
	except:
		return None


@ensure_csrf_cookie
@api_view(["POST"])		
def google_login_by_id_token(request):
	id_token = request.data.get("token")
	if not id_token: 
		return Response({"error": "token is required"}, status = bad_request)
			
	data = verify_id_token(id_token)	
	if not data: 
		return Response({"error": "Invalid token"}, status = bad_request)
			
	email = data.get("email")
	first_name = data.get("given_name")
	last_name = data.get("family_name")
	
	if not email:
		return Response({"error": "Unable to get email from Google account"}, status = bad_request)
				
	try: 
		user = User.objects.get(email = email)
		if not user.is_active: 
			raise User.DoesNotExist
		new_user = False
	except User.DoesNotExist:
		user = User.objects.create_user(
			username = email.rstrip("@gmail.com"), 
			email = email, 
			password = f'pass_{token_hex(32)}',
			first_name = first_name,
			last_name = last_name
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

@ensure_csrf_cookie
@api_view(["POST"])	
def google_login_by_code_token(request): 
	code = request.data.get("code")
	if not code: 
		return Response({"error": "No code provided"}, status = bad_request)
		
	token = client.fetch_token("https://oauth2.googleapis.com/token", code = code)
	id_token = token.get("id_token")
	id_info = verify_id_token(id_token)
	email = id_info.get("email")
	first_name = id_info.get("given_name")
	last_name = id_info.get("family_name")
	
	if not email:
		return Response({"error": "Unable to get email from Google account"}, status = bad_request)
				
	try: 
		user = User.objects.get(email = email)
		if not user.is_active: 
			raise User.DoesNotExist
		new_user = False
	except User.DoesNotExist:
		user = User.objects.create_user(
			username = email.rstrip("@gmail.com"), 
			email = email, 
			password = f'pass_{token_hex(32)}',
			first_name = first_name,
			last_name = last_name
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
	
@ensure_csrf_cookie
@api_view(["POST"])
def loginView(request): 
	serializer = LoginSerializer(data = request.data)
	if not serializer.is_valid():
		return Response(serializer.errors, status = bad_request)
	
	username = serializer.validated_data.get("username")
	email = serializer.validated_data.get("email")
	password = serializer.validated_data.get("password")
	
	try:
		user = User.objects.get(Q(username = username) | Q(email = email))
	except User.DoesNotExist:
		return Response({"error": "Unable to login with provided credentials"}, status = unauthorized)
	
	if not user.is_active:
		return Response({"error": "User is not verified"}, status = forbidden)
		
	if not user.check_password(password):
		return Response({"error": "Unable to login with provided credentials"}, status = unauthorized)
		
	refresh_token = RefreshToken.for_user(user)
	response = Response({
		"access": str(refresh_token.access_token),
		"user" : {
			"id": user.id,
			"username": user.username,
			"email": user.email,
			"firstname": user.first_name,
			"lastname": user.last_name
		}
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
	
		
@csrf_protect
@api_view(["GET"])	    
def logoutView(request):
	refresh_token = request.COOKIES.get("refresh_token")
	if not refresh_token: 
			return Response({"error": "You don't have permission to use this view"}, status = unauthorized)
	try: 
		token = RefreshToken(refresh_token)
		token.blacklist()
		response = Response(status = status.HTTP_205_RESET_CONTENT)
		response.delete_cookie("refresh_token")
		return response
	except:
		return Response({"error": "invalid token"}, status = bad_request)

		
@method_decorator(csrf_protect, name = "dispatch")
class CustomTokenRefreshView(TokenRefreshView): 
	def post(self, request, *args, **kwargs):
		refresh_token = request.COOKIES.get("refresh_token")
		if not refresh_token: 
			return Response({"error": "You don't have permission to use this view"}, status = unauthorized)
		request._full_data = MultiValueDict({"refresh": [refresh_token]})
		response = super().post(request, *args, **kwargs)
		if "refresh" in response.data: 
			new_refresh_token = response.data.pop("refresh")
			response.set_cookie(
			    key = "refresh_token",
			    value = new_refresh_token,
			    secure = True,
			    httponly = True,
			    max_age = 60 * 60 * 24 * 30,
			    samesite = 'None'
			)
			
		return response