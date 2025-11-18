#!/bin/bash
set -e

echo "Running migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

printenv > /etc/environment

echo "Testing refresh_clan command..."
python manage.py refresh_clan || echo "Initial refresh test completed"

echo "Setting up cron jobs..."
python manage.py crontab remove || true
python manage.py crontab add

echo "Installed cron jobs:"
crontab -l

echo "Starting cron daemon..."
cron

echo "Tailing cron log in background..."
tail -f /var/log/cron.log &

echo "Starting Gunicorn..."
exec gunicorn clashstats_v2.wsgi:application --bind 0.0.0.0:8000 --workers 4