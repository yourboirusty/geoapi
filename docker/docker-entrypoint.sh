#!/bin/sh

set -e

# activate our virtual environment here
. /opt/pysetup/.venv/bin/activate

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec "$@"
