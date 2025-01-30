#!/bin/sh

# Run migrations
uv run manage.py migrate

# Collect static files
uv run manage.py collectstatic --noinput

# compile messages for translation
uv run manage.py compilemessages -l uk

# Check environment variable
if [ "$ENVIRONMENT" = "development" ]; then
    # Start Django development server
    exec uv run manage.py runserver 0.0.0.0:8000
else
    # Start Gunicorn server
    exec uv run gunicorn --timeout 120 --bind 0.0.0.0:$PORT --access-logfile - ruchky_backend.asgi:application -k ruchky_backend.workers.UvicornWorker
fi
