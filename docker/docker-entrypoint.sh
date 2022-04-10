#!/bin/sh

set -e

# activate our virtual environment here
. /opt/pysetup/.venv/bin/activate

python manage.py migrate --noinput
python manage.py collectstatic --noinput

python manage.py user_exists || python manage.py loadddata fixtures/seed.json

exec "$@"
