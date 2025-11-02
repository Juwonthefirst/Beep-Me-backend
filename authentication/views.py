import json
import re
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
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
from authentication.serializers import LoginSerializer, SignupSerializer
from authentication.services import send_user_otp
from BeepMe.utils import cookify_response_tokens
from user.serializers import CurrentUserSerializer
import os
import secrets
import hashlib
from BeepMe.cache import cache
from asgiref.sync import async_to_sync

User = get_user_model()
bad_request = status.HTTP_400_BAD_REQUEST
unauthorized = status.HTTP_401_UNAUTHORIZED
forbidden = status.HTTP_403_FORBIDDEN
google_client_id = os.getenv("GOOGLE_CLIENT_ID")
google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
client = OAuth2Session(
    google_client_id, google_client_secret, redirect_uri="postmessage"
)


def verify_id_token(token):
    try:
        return id_token.verify_oauth2_token(token, requests.Request())
    except:
        return None


# @ensure_csrf_cookie
# @api_view(["POST"])
# def google_login_by_id_token(request):
#     id_token = request.data.get("token")
#     if not id_token:
#         return Response({"error": "token is required"}, status=bad_request)

#     data = verify_id_token(id_token)
#     if not data:
#         return Response({"error": "Invalid token"}, status=bad_request)

#     email = data.get("email")
#     first_name = data.get("given_name")
#     last_name = data.get("family_name")

#     if not email:
#         return Response(
#             {"error": "Unable to get email from Google account"}, status=bad_request
#         )

#     try:
#         user = User.objects.get(email=email)
#         if not user.is_active:
#             raise User.DoesNotExist
#         new_user = False
#     except User.DoesNotExist:
#         user = User.objects.create_user(
#             username=email.rstrip("@gmail.com"),
#             email=email,
#             password=f"pass_{token_hex(32)}",
#             first_name=first_name,
#             last_name=last_name,
#         )
#         new_user = True

#     refresh_token = RefreshToken.for_user(user)

#     response = Response(
#         {
#             "access": str(refresh_token.access_token),
#             "user": CurrentUserSerializer(user).data,
#             "new_user": new_user,
#         }
#     )

#     response.set_cookie(
#         key="refresh_token",
#         value=str(refresh_token),
#         secure=True,
#         httponly=True,
#         max_age=60 * 60 * 24 * 30,
#         samesite="None",
#     )

#     return response


@cookify_response_tokens
@ensure_csrf_cookie
@api_view(["POST"])
@permission_classes([AllowAny])
def google_login_by_code_token(request):
    code = request.data.get("code")
    if not code:
        return Response({"error": "No code provided"}, status=bad_request)

    token = client.fetch_token("https://oauth2.googleapis.com/token", code=code)
    id_token = token.get("id_token")
    id_info = verify_id_token(id_token)
    email = id_info.get("email")
    first_name = id_info.get("given_name")
    last_name = id_info.get("family_name")

    if not email:
        return Response(
            {"error": "Unable to get email from Google account"}, status=bad_request
        )

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        user = User.objects.create_user(
            username=email.rstrip("@gmail.com"),
            email=email,
            password=f"pass_{token_hex(32)}",
            first_name=first_name,
            last_name=last_name,
        )

    refresh_token = RefreshToken.for_user(user)
    return Response(
        {
            "refresh": str(refresh_token),
            "access": str(refresh_token.access_token),
            "user": CurrentUserSerializer(user).data,
        }
    )


@cookify_response_tokens
@ensure_csrf_cookie
@api_view(["POST"])
@permission_classes([AllowAny])
def loginView(request):
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=bad_request)

    identification = serializer.validated_data.get("identification")
    password = serializer.validated_data.get("password")

    try:
        if re.fullmatch(settings.USERNAME_REGEX, identification):
            user = User.objects.get(username=identification)
        elif "@" in identification and "." in identification:
            user = User.objects.get(email=identification)
        else:
            raise ValueError

    except (User.DoesNotExist, ValueError):
        return Response(
            {"error": "Unable to login with provided credentials"}, status=bad_request
        )

    if not user.check_password(password):
        return Response(
            {"error": "Unable to login with provided credentials"}, status=bad_request
        )

    refresh_token = RefreshToken.for_user(user)
    return Response(
        {
            "user": CurrentUserSerializer(user).data,
            "refresh": str(refresh_token),
            "access": str(refresh_token),
        }
    )


@csrf_protect
@api_view(["GET"])
def logoutView(request):
    refresh_token = request.COOKIES.get("refresh_token")
    if not refresh_token:
        return Response(
            {"error": "You don't have permission to use this view"}, status=unauthorized
        )
    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
        response = Response(status=status.HTTP_205_RESET_CONTENT)
        response.delete_cookie("refresh_token")
        response.delete_cookie("access_token")
        return response
    except:
        return Response({"error": "invalid token"}, status=bad_request)


@method_decorator(cookify_response_tokens, name="post")
@method_decorator(csrf_protect, name="dispatch")
@method_decorator(permission_classes([AllowAny]), name="dispatch")
class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            return Response(
                {"error": "You don't have permission to use this view"},
                status=unauthorized,
            )
        request._full_data = MultiValueDict({"refresh": [refresh_token]})
        try:
            return super().post(request, *args, **kwargs)
        except User.DoesNotExist:
            return Response({"error": "user doesn't exist"}, status=bad_request)


@method_decorator(ensure_csrf_cookie, name="dispatch")
class RetrieveOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        if User.objects.filter(email=email).exists():
            return Response({"error": "email taken"}, status=bad_request)

        session_id = secrets.token_urlsafe(32)
        otp = "".join([str(secrets.randbelow(10)) for _ in range(6)])
        otp_hash = hashlib.sha256(otp.encode()).hexdigest()

        async_to_sync(cache.set_hash)(
            f"signup_session:{session_id}",
            mapping={
                "email": email,
                "otp_hash": otp_hash,
                "verified": 0,
                "attempts": 0,
            },
            expiry_time=600,
        )

        send_user_otp(otp, to=email)
        response = Response({"status": "sent"})
        response.set_cookie(
            "signup_session_id",
            session_id,
            secure=os.getenv("ENVIROMENT") == "production",
            httponly=True,
            max_age=60 * 10,
            samesite="None",
        )
        return response


@method_decorator(ensure_csrf_cookie, name="post")
class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        session_id = request.COOKIES.get("signup_session_id")
        user_otp = request.data.get("otp")

        session = json.loads(
            async_to_sync(cache.get_hash)(f"signup_session:{session_id}")
        )
        if not session:
            return Response({"error": "Invalid session"}, status=bad_request)

        if session["attempts"] >= 5:
            async_to_sync(cache.delete)(f"signup_session:{session_id}")
            return Response(
                {"error": "Too many attempts"}, status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        user_hash = hashlib.sha256(user_otp.encode()).hexdigest()

        if secrets.compare_digest(session["otp_hash"], user_hash):
            async_to_sync(cache.set_hash_field)(
                f"signup_session:{session_id}", "verified", 1
            )
            async_to_sync(cache.delete_hash_field)(
                f"signup_session:{session_id}", "otp_hash"
            )
            return Response({"status": "verified"})
        else:
            session["attempts"] += 1
            async_to_sync(cache.set)(
                f"signup_session:{session_id}", session, expiry_time=600
            )
            return Response({"error": "Invalid code"}, status=bad_request)


@method_decorator(cookify_response_tokens, name="post")
@method_decorator(ensure_csrf_cookie, name="post")
class CompleteSignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=bad_request)

        session_id = request.COOKIES.get("signup_session_id")
        username = serializer.validated_data.get("username")
        password = serializer.validated_data.get("password")

        is_session_verified = async_to_sync(cache.get_hash_field)(
            f"signup_session:{session_id}", "verified"
        )
        if not is_session_verified:
            return Response({"error": "Not verified"}, status=bad_request)

        user_email = async_to_sync(cache.get_hash_field)(
            f"signup_session:{session_id}", "email"
        )
        async_to_sync(cache.delete)(f"signup_session:{session_id}")

        if User.objects.filter(email=user_email).exists():
            return Response({"error": "email taken"}, status=bad_request)

        if User.objects.filter(username=username).exists():
            return Response({"error": "username taken"}, status=bad_request)

        try:
            user = User.objects.create_user(
                username=username, email=user_email, password=password
            )

            refresh_token = RefreshToken.for_user(user)
            return Response(
                {
                    "refresh": str(refresh_token),
                    "access": str(refresh_token.access_token),
                    "user": CurrentUserSerializer(user).data,
                }
            )
        except Exception as e:
            return Response({"error": str(e)}, status=bad_request)
