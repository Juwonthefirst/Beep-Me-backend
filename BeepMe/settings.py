from .utils import load_enviroment_variables

load_enviroment_variables()

from pathlib import Path
from datetime import timedelta
import os, dj_database_url


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/
DEBUG = True
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")
# SECURITY WARNING: don't run with debug turned on in production!
ALLOWED_HOSTS = [os.getenv("HOST_NAME"), "localhost"]


# Application definition
INSTALLED_APPS = [
    "daphne",
    "channels",
    "django.contrib.sites",
    "django.contrib.admin",
    "django.contrib.messages",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "adrf",
    "drf_yasg",
    "authentication",
    "user",
    "message",
    "group",
    "notification",
    "chat_room",
    "upload",
]

if DEBUG:
    INSTALLED_APPS += ["corsheaders"]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.contrib.sites.middleware.CurrentSiteMiddleware",
]

if DEBUG:
    MIDDLEWARE += ["corsheaders.middleware.CorsMiddleware"]

ROOT_URLCONF = "BeepMe.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "BeepMe.wsgi.application"
ASGI_APPLICATION = "BeepMe.asgi.application"

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    "default": dj_database_url.config(
        default=os.getenv("DATABASE_URL"),
        conn_max_age=600,
    )
}


AUTH_USER_MODEL = "user.CustomUser"
# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_FILTER_BACKENDS": ["rest_framework.filters.SearchFilter"],
}

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.BCryptPasswordHasher",
]

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=20),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
}

DJOSER = {
    "TOKEN_MODEL": None,
    "EMAIL_FRONTEND_PROTOCOL": "https",
    "EMAIL_FRONTEND_DOMAIN": os.getenv("FRONTEND_HOST_NAME"),
    "EMAIL_FRONTEND_SITE_NAME": "Beep",
    "SEND_ACTIVATION_EMAIL": True,
    "SEND_CONFIRMATION_EMAIL": True,
    "PASSWORD_CHANGED_EMAIL_CONFIRMATION": True,
    "ACTIVATION_URL": "verify-email/?uid={uid}&token={token}",
    "LOGOUT_ON_PASSWORD_CHANGE": True,
}

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")


CORS_ALLOW_ALL_ORIGINS = True

CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    os.getenv("HOST_DOMAIN"),
]


CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [
                {
                    "address": os.getenv("REDIS_URL"),
                },
            ],
        },
    }
}

# CACHES = {
#     "default": {
#         "BACKEND": "django_redis.cache.RedisCache",
#         "LOCATION": os.getenv("REDIS_URL"),
#         "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient", "SSL": True},
#     }
# }


USERNAME_REGEX = r"^[a-zA-Z](?:[a-zA-Z0-9]*(?:[-_][a-zA-Z0-9])?)*[a-zA-Z0-9]+$"
OTP_EXPIRY_TIME = 600

# Storage
PUBLIC_BUCKET_ACCESS_KEY = os.getenv("PUBLIC_BUCKET_ACCESS_KEY")
PUBLIC_BUCKET_SECRET_KEY = os.getenv("PUBLIC_BUCKET_SECRET_KEY")
PUBLIC_BUCKET_NAME = os.getenv("PUBLIC_BUCKET_NAME")
PUBLIC_BUCKET_ENDPOINT_URL = os.getenv("PUBLIC_BUCKET_ENDPOINT")
PUBLIC_BUCKET_PUBLIC_ENDPOINT_URL = os.getenv("PUBLIC_BUCKET_PUBLIC_ENDPOINT")

PRIVATE_BUCKET_NAME = os.getenv("PRIVATE_BUCKET_NAME")
PRIVATE_BUCKET_ENDPOINT_URL = os.getenv("PRIVATE_BUCKET_ENDPOINT")
PRIVATE_BUCKET_ACCESS_KEY = os.getenv("PRIVATE_BUCKET_ACCESS_KEY")
PRIVATE_BUCKET_SECRET_KEY = os.getenv("PRIVATE_BUCKET_SECRET_KEY")


if os.getenv("ENVIROMENT") == "production":
    ALLOWED_HOSTS.append(os.getenv("FRONTEND_HOST_NAME"))
    DEBUG = False
    STORAGES = {
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
        },
    }

    DATABASES["default"]["OPTIONS"] = {
        "sslmode": "require",
    }

    CSRF_TRUSTED_ORIGINS = [
        os.getenv("HOST_DOMAIN"),
        "https://" + os.getenv("FRONTEND_HOST_NAME"),
    ]

    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    CSRF_COOKIE_SAMESITE = "None"
    SESSION_COOKIE_SAMESITE = "None"
