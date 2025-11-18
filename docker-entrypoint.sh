#!/bin/bash
set -e

echo "Running migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "Setting up cron jobs with environment variables..."
# Remove old cron jobs
python manage.py crontab remove || true

# Export all environment variables to a file that cron can source
printenv | grep -v "no_proxy" > /etc/environment

# Add cron jobs
python manage.py crontab add

echo "Installed cron jobs:"
crontab -l

echo "Starting cron daemon..."
cron

echo "Tailing cron log in background..."
tail -f /var/log/cron.log &

echo "Starting Gunicorn..."
exec gunicorn clashstats_v2.wsgi:application --bind 0.0.0.0:8000 --workers 4