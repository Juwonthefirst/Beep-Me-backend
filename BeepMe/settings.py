from pathlib import Path
from datetime import timedelta
import os, dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/
DEBUG = False
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
ALLOWED_HOSTS = [os.getenv("HOST_NAME"), "localhost", os.getenv("FRONTEND_HOST_NAME")]


# Application definition
INSTALLED_APPS = [
    "daphne",
    "channels",
    "django.contrib.sites",
    'django.contrib.admin',
    "django.contrib.messages",
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "dj_rest_auth",
    "dj_rest_auth.registration",
    "corsheaders",
    "storages",
    "drf_yasg",
    "user",
    "authentication",
    "home",
    "chat_room",
    "message",
    "group",
    "notification",
    "upload"
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    "corsheaders.middleware.CorsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "allauth.account.middleware.AccountMiddleware",
	'django.contrib.sites.middleware.CurrentSiteMiddleware',
]

ROOT_URLCONF = 'BeepMe.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'BeepMe.wsgi.application'
ASGI_APPLICATION = 'BeepMe.asgi.application'

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv("DATABASE_URL"),
        conn_max_age = 600,
    )
}

DATABASES["default"]["OPTIONS"] = {
    "sslmode": "require",
}

AUTH_USER_MODEL = "user.CustomUser"
# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

ACCOUNT_ADAPTER = "authentication.adapters.EmailAdapter"
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_UNIQUE_EMAIL = True

ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_LOGIN_METHODS = {"username", "email"}
ACCOUNT_SIGNUP_FIELDS = ["username*","email*", "password1*", "password2*"]

REST_FRAMEWORK = {
	"DEFAULT_AUTHENTICATION_CLASSES": (
		"rest_framework_simplejwt.authentication.JWTAuthentication",
		"rest_framework.authentication.BasicAuthentication"
	),
	"DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
	"PAGE_SIZE": 50
}

PASSWORD_HASHERS = [
	"django.contrib.auth.hashers.Argon2PasswordHasher",
	"django.contrib.auth.hashers.PBKDF2PasswordHasher",
	"django.contrib.auth.hashers.BCryptPasswordHasher"
]

SIMPLE_JWT ={
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes = 60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days = 30),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True
}

REST_AUTH = {
    "USE_JWT": True,
    "TOKEN_MODEL": None,
    "JWT_AUTH_COOKIE": None,
    "JWT_AUTH_REFRESH_COOKIE": None,
    "JWT_AUTH_HTTPONLY": False
}

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD =  os.getenv("EMAIL_HOST_PASSWORD")

CORS_ALLOWED_ORIGINS = [
    "https://" + os.getenv("HOST_NAME"),
    "http://localhost:7700",
    "https://" + os.getenv("FRONTEND_HOST_NAME")
]

CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = [
    "https://" + os.getenv("HOST_NAME"),
    "http://localhost:7700",
    "https://" + os.getenv("FRONTEND_HOST_NAME")
]

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = 'None'
SESSION_COOKIE_SAMESITE = 'None'


CHANNEL_LAYERS = {
    "default":{
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG":{
            "hosts":[os.getenv("REDIS_URL")],
        },
    }
}

CACHES = {
	'default': {
		'BACKEND': 'django_redis.cache.RedisCache',
		'LOCATION': os.getenv("REDIS_URL"),
		'OPTIONS': {
			'CLIENT_CLASS': 'django_redis.client.DefaultClient',
			'SSL': True
		}
	}
}

#Storage
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
AWS_ACCESS_KEY_ID = ""
AWS_SECRET_ACCESS_KEY = ""
AWS_STORAGE_BUCKET_NAME = ""
AWS_S3_ENDPOINT_URL = ""
AWS_S3_FILE_OVERWRITE = True
AWS_S3_REGION_NAME = "auto"
AWS_DEFAULT_ACL = None
AWS_S3_VERIFY = True
AWS_S3_USE_SSL = True
