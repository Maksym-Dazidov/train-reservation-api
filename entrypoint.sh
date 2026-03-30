#!/bin/sh

set -e

echo "Waiting for database..."

DB_HOST=$(python -c "import os; from urllib.parse import urlparse; print(urlparse(os.environ['DATABASE_URL']).hostname)")
DB_PORT=$(python -c "import os; from urllib.parse import urlparse; u=urlparse(os.environ['DATABASE_URL']); print(u.port or 5432)")


while ! nc -z $DB_HOST $DB_PORT; do
  sleep 1
done

echo "Database started"

python manage.py migrate --noinput

python manage.py collectstatic --noinput

CPU_CORES=$(nproc)

WORKERS=$((2 * CPU_CORES + 1))
export GUNICORN_WORKERS=$WORKERS

echo "Starting Gunicorn with $GUNICORN_WORKERS workers"

exec gunicorn train_reservation_api.wsgi:application \
     --bind 0.0.0.0:8000 \
     --workers $GUNICORN_WORKERS \
     --timeout 60 \
     --graceful-timeout 30 \
     --max-requests 500 \
     --max-requests-jitter 50
