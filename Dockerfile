FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps for psycopg2, etc.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
  && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies first (better build cache)
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the rest of the project
COPY . /app

EXPOSE 8000

ENV DJANGO_SETTINGS_MODULE=clashstats_v2.settings

CMD ["sh", "-c", "python manage.py migrate && gunicorn clashstats_v2.wsgi:application --bind 0.0.0.0:8000"]