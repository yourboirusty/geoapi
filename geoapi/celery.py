from celery import Celery
import os

# TODO: Add visibility
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "geoapi.settings")

app = Celery("geoapi")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

if __name__ == "__main__":
    app.start()
