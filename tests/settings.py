import os
from pathlib import Path
from geoapi.settings import *  # noqa F401

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

DEBUG = True

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


CELERY_BROKER_URL = "memory://localhost/"
CELERY_RESULT_URL = "memory://localhost/"
CELERY_RESULT_EXTENDED = True
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_DEFAULT_RETRY_DELAY = 1

IPSTACK_KEY = os.environ.get("IPSTACK_KEY", "invalidkey")
