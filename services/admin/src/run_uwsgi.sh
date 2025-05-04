#!/bin/sh

if [ ! -f /tmp/.initialized ]; then
    echo "Performing initial setup..."

    python manage.py migrate contenttypes
    python manage.py migrate sessions
    python manage.py migrate auth
    python manage.py migrate admin
    python manage.py migrate movies 0001_initial --fake
    python manage.py createsuperuser --noinput

    touch /tmp/.initialized
    echo "Initial setup complete"
fi

echo "Performing migrations..."
python manage.py migrate
echo "Migrations finished"

echo "Collecting static files..."
python manage.py collectstatic --noinput
echo "Static files collected"

echo "Starting the server..."
uwsgi --ini uwsgi.ini
