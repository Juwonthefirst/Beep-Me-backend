from django.conf import settings
from django.core.mail import send_mail
from BeepMe.utils import background_task
from google.oauth2 import id_token
from google.auth.transport import requests
import hashlib
import secrets
from BeepMe.cache import cache
from asgiref.sync import async_to_sync


@background_task
def send_user_otp(otp, to):
    send_mail(
        "Your verification code",
        f"Your code is: {otp}",
        "noreply@beep.com",
        [to],
    )


def verify_google_id_token(token):
    try:
        return id_token.verify_oauth2_token(token, requests.Request())
    except Exception as e:
        print(f"Google ID token verification failed: {e}")
        return None


def generateOTP():
    otp = "".join([str(secrets.randbelow(10)) for _ in range(6)])
    otp_hash = hashlib.sha256(otp.encode()).hexdigest()

    return [otp, otp_hash]


def create_email_verification_session(
    email: str,
    is_google_auth: bool = False,
    otp_hash: str | None = None,
):
    session_id = secrets.token_urlsafe(32)
    session_data = {
        "email": email,
        "verified": int(is_google_auth),
        "is_google_auth": int(is_google_auth),
        "attempts": 0,
    }

    if otp_hash:
        session_data["otp_hash"] = otp_hash

    async_to_sync(cache.set_hash)(
        f"signup_session:{session_id}",
        mapping=session_data,
        expiry_time=settings.OTP_EXPIRY_TIME,
    )

    return session_id
