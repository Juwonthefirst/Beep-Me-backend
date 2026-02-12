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
from django.db import transaction
from django.utils.decorators import method_decorator
from django.utils.datastructures import MultiValueDict
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect

from authlib.integrations.requests_client import OAuth2Session
from authentication.serializers import LoginSerializer, SignupSerializer
from authentication.services import (
    create_email_verification_session,
    generateOTP,
    send_user_otp,
    verify_google_id_token,
)
from BeepMe.utils import build_absolute_uri, cookify_response_tokens
from BeepMe.storage import public_storage
from user.models import CustomUser
from user.serializers import CurrentUserSerializer
import os
import secrets
import hashlib
from BeepMe.cache import cache
from asgiref.sync import async_to_sync

User = get_user_model()
bad_request = status.HTTP_400_BAD_REQUEST
unauthorized = status.HTTP_401_UNAUTHORIZED
conflict = status.HTTP_409_CONFLICT
forbidden = status.HTTP_403_FORBIDDEN

google_client_id = os.getenv("GOOGLE_CLIENT_ID")
google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
client = OAuth2Session(
    google_client_id, google_client_secret, redirect_uri="postmessage"
)

cookify_auth_tokens = cookify_response_tokens(
    {
        "refresh_token": {
            "max_age": settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()
        },
        "access_token": {
            "max_age": settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()
        },
    },
)

cookify_signup_tokens = cookify_response_tokens(
    {
        "pending_google_signup": {"max_age": settings.OTP_EXPIRY_TIME},
        "signup_session_id": {"max_age": settings.OTP_EXPIRY_TIME},
    }
)


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


@cookify_signup_tokens
@cookify_auth_tokens
@ensure_csrf_cookie
@api_view(["POST"])
@permission_classes([AllowAny])
def google_login_by_code_token(request):
    code = request.data.get("code")
    if not code:
        return Response({"error": "No code provided"}, status=bad_request)

    try:

        token = client.fetch_token("https://oauth2.googleapis.com/token", code=code)
        id_token = token.get("id_token")
        id_info = verify_google_id_token(id_token)
        email: str = id_info.get("email")
    except:
        return Response({"error": "Unable to connect to Google"}, status=bad_request)

    if not email:
        return Response(
            {"error": "Unable to get email from Google account"}, status=bad_request
        )

    try:
        user = User.objects.get(email=email)
        refresh_token = RefreshToken.for_user(user)
        return Response(
            {
                "refresh_token": str(refresh_token),
                "access_token": str(refresh_token.access_token),
                "user": CurrentUserSerializer(user).data,
            }
        )
    except User.DoesNotExist:
        session_id = async_to_sync(create_email_verification_session)(
            email, is_google_auth=True
        )
        return Response(
            {"signup_session_id": session_id, "pending_google_signup": True}
        )


@cookify_auth_tokens
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
            user = User.objects.get(username=identification.capitalize())
        elif "@" in identification and "." in identification:
            user = User.objects.get(email=identification.lower())
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
            "refresh_token": str(refresh_token),
            "access_token": str(refresh_token.access_token),
        }
    )


# @csrf_protect
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


@method_decorator(cookify_auth_tokens, name="post")
# @method_decorator(csrf_protect, name="dispatch")
class CustomTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            return Response(
                {"error": "You don't have permission to use this view"},
                status=unauthorized,
            )
        request._full_data = MultiValueDict({"refresh": [refresh_token]})
        try:
            response = super().post(request, *args, **kwargs)
            access_token = response.data.pop("access")
            refresh_token = response.data.pop("refresh")
            response.data = {
                "refresh_token": refresh_token,
                "access_token": access_token,
            }

            return response
        except User.DoesNotExist:
            response = Response({"error": "user doesn't exist"}, status=bad_request)
            response.delete_cookie("refresh_token")
            return response


@method_decorator(ensure_csrf_cookie, name="dispatch")
@method_decorator(cookify_signup_tokens, name="post")
class RetrieveOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email", "").lower()
        if not email:
            return Response({"error": "No email provided"}, status=bad_request)

        if User.objects.filter(email=email).exists():
            return Response(
                {"error": "This email is already in use"}, status=bad_request
            )

        if request.COOKIES.get("signup_session_id"):
            async_to_sync(cache.delete)(
                f"signup_session:{request.COOKIES.get('signup_session_id')}"
            )

        [otp, otp_hash] = generateOTP()
        session_id = async_to_sync(create_email_verification_session)(
            email, otp_hash=otp_hash
        )

        send_user_otp(otp, to=email)
        return Response({"status": "sent", "signup_session_id": session_id})


# @method_decorator(csrf_protect, name="post")
class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        session_id = request.COOKIES.get("signup_session_id")
        user_otp = request.data.get("otp")
        session = async_to_sync(cache.get_hash)(f"signup_session:{session_id}")

        if not session:
            return Response({"error": "Invalid session"}, status=bad_request)

        if int(session["attempts"]) >= 5:
            async_to_sync(cache.delete)(f"signup_session:{session_id}")
            return Response(
                {"error": "Too many attempts, Request for a new token"},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        user_hash = hashlib.sha256(user_otp.encode()).hexdigest()
        if secrets.compare_digest(session["otp_hash"], user_hash):
            async_to_sync(cache.set_hash_field)(
                f"signup_session:{session_id}", "verified", 1
            )
            async_to_sync(cache.delete_hash_field)(
                f"signup_session:{session_id}", "otp_hash"
            )
            async_to_sync(cache.set_expire_time)(
                f"signup_session:{session_id}", 20 * 60
            )

            return Response({"status": "verified"})
        else:
            async_to_sync(cache.increase_hash_field)(
                f"signup_session:{session_id}", "attempts"
            )
            return Response({"error": "Wrong OTP code"}, status=bad_request)


@method_decorator(cookify_auth_tokens, name="post")
# @method_decorator(csrf_protect, name="post")
class CompleteSignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=bad_request)

        session_id = request.COOKIES.get("signup_session_id")
        username = serializer.validated_data.get("username")
        profile_picture = serializer.validated_data.get("profile_picture", None)
        password = serializer.validated_data.get("password")

        signup_session: dict | None = async_to_sync(cache.get_hash)(
            f"signup_session:{session_id}",
        )
        if not (signup_session and signup_session.get("verified") == "1"):
            return Response({"error": "Not verified"}, status=bad_request)

        user_email: str = signup_session.get("email")
        is_google_auth: bool = signup_session.get("is_google_auth")

        if User.objects.filter(email=user_email).exists():
            return Response({"error": "email is already in use"}, status=conflict)

        if User.objects.filter(username=username).exists():
            return Response({"error": "username is already in use"}, status=conflict)

        if is_google_auth:
            password = f"pass_{secrets.token_hex(32)}"

        try:
            with transaction.atomic():
                user: CustomUser = User.objects.create_user(
                    username=username,
                    email=user_email,
                    password=password,
                )

                refresh_token = RefreshToken.for_user(user)
                new_user = CurrentUserSerializer(user).data
                profile_picture_upload_link = public_storage.generate_upload_url(
                    key=user.profile_picture
                )
                response = Response(
                    {
                        "refresh_token": str(refresh_token),
                        "access_token": str(refresh_token.access_token),
                        "user": new_user,
                        "avatar_upload_link": (
                            build_absolute_uri(profile_picture_upload_link)
                            if settings.DEBUG
                            else profile_picture_upload_link
                        ),
                    }
                )
                response.delete_cookie("signup_session_id")
                response.delete_cookie("pending_google_signup")
                async_to_sync(cache.delete)(f"signup_session:{session_id}")

            return response

        except Exception as e:
            return Response({"error": str(e)}, status=bad_request)
