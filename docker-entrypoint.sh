#!/bin/bash
set -e

echo "Running migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "Refreshing clan..."
python manage.py refresh_clan || echo "Initial refresh test completed"

echo "Setting up cron jobs..."
python manage.py crontab remove || true
python manage.py crontab add

echo "Starting cron daemon..."
cron

echo "Adding env var to crontab..."
printenv | grep -v "no_proxy" >> /etc/environment

echo "Starting Gunicorn..."
exec gunicorn clashstats_v2.wsgi:application --bind 0.0.0.0:8000 --workers 4