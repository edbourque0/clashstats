FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps + cron
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    cron \
  && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# App code
COPY . /app

EXPOSE 8000

ENV DJANGO_SETTINGS_MODULE=clashstats_v2.settings

CMD ["sh", "-c", "\
  python manage.py makemigrations && \
  python manage.py migrate && \
  ( python manage.py crontab remove || true ) && \
  python manage.py crontab add && \
  ( test -f /etc/cron.d/django_crontab && chmod 0644 /etc/cron.d/django_crontab || true ) && \
  service cron start && \
  gunicorn clashstats_v2.wsgi:application --bind 0.0.0.0:8000 --workers 4 \
"]