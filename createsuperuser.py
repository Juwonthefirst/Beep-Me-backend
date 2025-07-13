import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BeepMe.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

username = os.environ.get('DJANGO_SUPERUSER_USERNAME', os.getenv("USERNAME"))
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', os.getenv("EMAIL"))
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', os.getenv("PASSWORD"))

if not User.objects.filter(email=email).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Superuser '{username}' created.")
else:
    print(f"Superuser '{username}' already exists.")