from celery import Celery
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "geoapi.settings")

app = Celery("geoapi")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()

if __name__ == "__main__":
    app.start()
