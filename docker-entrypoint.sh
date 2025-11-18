#!/bin/bash
set -e

echo "Running migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

printenv > env.txt
cat /var/spool/cron/crontabs/root >> env.txt
cat env.txt > /var/spool/cron/crontabs/root

echo "Setting up cron jobs..."
python manage.py crontab remove || true
python manage.py crontab add

echo "Adding env var to crontab"
printenv > env.txt
cat /var/spool/cron/crontabs/root >> env.txt
cat env.txt > /var/spool/cron/crontabs/root

echo "Starting cron daemon..."
cron

echo "Starting Gunicorn..."
exec gunicorn clashstats_v2.wsgi:application --bind 0.0.0.0:8000 --workers 4