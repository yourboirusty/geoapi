web: daphne geoapi.asgi:application --bind 0.0.0.0 -p $PORT -v2
celeryworker: celery -A geoapi worker --loglevel=info
