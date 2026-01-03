#!/usr/bin/env bash
set -e

echo "🚀 Starting Django..."

echo "⏳ Waiting for database..."
until python - <<END
import socket, os
host = os.environ.get("DB_HOST")
port = int(os.environ.get("DB_PORT", 3306))
s = socket.socket()
s.settimeout(3)
try:
    s.connect((host, port))
    s.close()
except Exception:
    exit(1)
END
do
  echo "Database not ready, retrying..."
  sleep 3
done

echo "📦 Applying migrations..."
python manage.py migrate --noinput

echo "🎨 Collecting static files..."
python manage.py collectstatic --noinput

echo "🔥 Starting Gunicorn..."
exec gunicorn gowheels_project.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers "${GUNICORN_WORKERS:-3}" \
  --timeout 120
