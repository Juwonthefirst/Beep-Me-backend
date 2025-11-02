from django.contrib.auth import get_user_model

User = get_user_model()


def is_username_taken(username):
    return User.objects.filter(username=username).exists()
