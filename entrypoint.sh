#!/bin/sh
set -e

echo "Creating static files directory if it doesn't exist..."
mkdir -p /app/staticfiles

echo "Running collectstatic..."
python manage.py collectstatic --noinput

echo "Running migrations..."
python manage.py migrate

echo "Starting Gunicorn..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000
