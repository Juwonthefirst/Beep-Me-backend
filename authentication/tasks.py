from celery import shared_task
from django.core.mail import send_mail


@shared_task
def send_user_otp(otp, to):
    send_mail(
        "Your verification code",
        f"Your code is: {otp}",
        "noreply@yoursite.com",
        [to],
    )
