#!/bin/sh
set -eu
python manage.py migrate --noinput
if [ "${SEED_DEMO:-false}" = "true" ]; then
    python manage.py seed_demo
fi
exec gunicorn comission_project.wsgi:application --bind "0.0.0.0:${PORT:-10000}" --workers 1 --threads 2 --timeout 120 --access-logfile -
