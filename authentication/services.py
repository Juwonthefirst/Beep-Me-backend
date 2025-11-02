from django.core.mail import send_mail

from BeepMe.utils import background_task


@background_task
def send_user_otp(otp, to):
    send_mail(
        "Your verification code",
        f"Your code is: {otp}",
        "noreply@beep.com",
        [to],
    )
