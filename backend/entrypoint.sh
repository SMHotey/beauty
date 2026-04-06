#!/bin/bash
set -e

echo "Waiting for PostgreSQL..."
while ! nc -z ${DB_HOST:-db} ${DB_PORT:-5432}; do
  sleep 0.1
done
echo "PostgreSQL started"

python manage.py migrate --noinput
python manage.py collectstatic --noinput --clear
python manage.py loaddata fixtures/initial_data.json || true

exec gunicorn beauty_backend.wsgi:application --bind 0.0.0.0:8000 --workers 3
