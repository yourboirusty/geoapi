import os
from pathlib import Path
import string

# TODO: Start using dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    "DANGO_SECRET",
    "django-insecure-)f4#vrs0b%)o-^8uhim#3c_x1e!61^%xq_s-i)$zo&ag$hj*d&",
)

SLUG_CHARACTERS = string.ascii_uppercase + string.digits[2:]

DEBUG = os.environ.get("DEBUG", True)

REDIS_ADDRESS = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", "")
REDIS_USER = os.environ.get("REDIS_USER", "")

if not (REDIS_URL := os.environ.get("REDIS_URL")):
    REDIS_URL = (
        f"redis://{REDIS_USER}:{REDIS_PASSWORD}@{REDIS_ADDRESS}:{REDIS_PORT}/0"
    )

ALLOWED_HOSTS = [
    "*",
]

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.pubsub.RedisPubSubChannelLayer",
        "CONFIG": {
            "hosts": [(REDIS_URL)],
        },
    },
}


DEPENDENCIES = [
    "channels",
    "django_filters",
    "rest_framework",
    "drf_spectacular",
    "drf_spectacular_sidecar",
    "django_extensions",
]

PROJECT_APPS = [
    "data",
    "authentication",
]

INSTALLED_APPS = (
    [
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
    ]
    + DEPENDENCIES
    + PROJECT_APPS
)

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


SPECTACULAR_SETTINGS = {
    "TITLE": "GeoAPI",
    "SERVE_INCLUDE_SCHEMA": True,
    "SWAGGER_UI_DIST": "SIDECAR",  # shorthand to use the sidecar instead
    "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
    "REDOC_DIST": "SIDECAR",
}

ROOT_URLCONF = "geoapi.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "geoapi.wsgi.application"

ASGI_APPLICATION = "geoapi.asgi.application"

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "USER": os.environ.get("POSTGRES_USER", "postgres"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", ""),
        "NAME": os.environ.get("POSTGRES_DB", "geoapi"),
        "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
        "PORT": os.environ.get("POSTGRES_PORT", 5432),
    }
}

if os.environ.get("DATABASE_URL"):
    import dj_database_url

    DATABASES["default"] = dj_database_url.config(
        conn_max_age=600, ssl_require=True
    )

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",  # noqa E501
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",  # noqa E501
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",  # noqa E501
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",  # noqa E501
    },
]

AUTH_USER_MODEL = "authentication.User"


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Europe/Warsaw"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = "/static/"

STATIC_ROOT = os.path.join(BASE_DIR, "static")

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

MAX_EXTERNAL_API_RETRIES = 4

REST_FRAMEWORK = {
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend"
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",  # noqa E501
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "PAGE_SIZE": 100,
}

# Clean up redis url for celery
REDIS_URL_CELERY = REDIS_URL

if REDIS_URL.split("//")[1].split("@")[0][-1] == ":":
    REDIS_URL_CELERY = "redis://" + REDIS_URL.split("@")[1]

CELERY_BROKER_URL = REDIS_URL_CELERY
CELERY_RESULT_BACKEND = REDIS_URL_CELERY
CELERY_RESULT_EXTENDED = True
CELERY_DEFAULT_RETRY_DELAY = 1
CELERY_MAX_RETRIES = 3

IPSTACK_KEY = os.environ.get("IPSTACK_KEY", "fake_key")
IPSTACK_URL = os.environ.get("IPSTACK_URL", "http://api.ipstack.com/")
