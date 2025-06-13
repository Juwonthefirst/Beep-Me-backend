from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from dj_rest_auth.views import LoginView
from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from secrets import token_hex
from google.oauth2 import id_token
from google.auth.transport import requests
from allauth.account.models import EmailAddress
from authlib.integrations.requests_client import OAuth2Session
import os


User = get_user_model()
bad_request = status.HTTP_400_BAD_REQUEST
google_client_id = os.getenv("GOOGLE_CLIENT_ID")
google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
client = OAuth2Session(google_client_id, google_client_secret, redirect_uri = "postmessage")


def verify_id_token(token):
	try:
		return id_token.verify_oauth2_token(token, requests.Request())
	except:
		return None


@ensure_csrf_cookie
@api_view(["POST"])		
def googleLoginByIdToken(request):
	id_token = request.data.get("token")
	if not id_token: 
		return Response({"error": "token is required"}, status = bad_request)
			
	data = verify_id_token(id_token)	
	if not data: 
		return Response({"error": "Invalid token"}, status = bad_request)
			
	email = data.get("email")
	first_name = data.get("given_name")
	last_name = dat.get("family_name")
	
	if not email:
		return Response({"error": "Unable to get email from Google account"}, status = bad_request)
				
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

@ensure_csrf_cookie
@api_view(["POST"])	
def googleLoginByCode(request): 
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
	
@method_decorator(ensure_csrf_cookie, name = "dispatch")
class CustomLoginView(LoginView): 
	def get_response(self): 
		original_response = super().get_response()
		refresh_token = original_response.data.pop("refresh")
		original_response.set_cookie(
		    key = "refresh_token",
		    value = refresh_token,
		    secure = True,
		    httponly = True,
		    max_age = 60 * 60 * 24 * 30,
		    samesite = 'None'
		)
		return original_response


@csrf_protect
@api_view(["GET"])	    
def logoutView(request):
	refresh_token = request.COOKIES.get("refresh_token")
	if not refresh_token: 
			return Response({"error": "You don't have permission to use this view"}, status = status.HTTP_401_UNAUTHORIZED)
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
	serializer_class = TokenRefreshSerializer
	
	def post(self, request, *ags, **kwargs):
		refresh_token = request.COOKIES.get("refresh_token")
		if not refresh_token:
			return Response({"error": "You don't have permission to use this view"}, status = status.HTTP_401_UNAUTHORIZED)
			
		serializer = self.get_serializer(data = {"refresh": refresh_token})
		serializer.is_valid(raise_exception = True)
		access_token = serializer.validated_data.get("access")
		return Response({"access": access_token})