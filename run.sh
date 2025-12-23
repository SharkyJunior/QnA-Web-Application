#!/bin/bash

# run.sh для Gunicorn + Django
set -e

echo "Starting Django with Gunicorn..."

# Ожидание базы данных
echo "Waiting for PostgreSQL..."
sleep 5
echo "PostgreSQL is ready!"

# Применение миграций
echo "Applying migrations..."
python manage.py migrate

# Сбор статических файлов
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Создание суперпользователя
echo "Creating superuser if needed..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
from app.models import Profile
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')
    Profile.objects.create(user=User.objects.get(username='admin'), nickname='admin', avatar_url='../../static/img/avatar_placeholders/0.svg')
    print('Superuser created')
else:
    print('Superuser already exists')
"

# echo "Filling the database..."
# python manage.py fill_db

# Запуск Gunicorn
echo "Starting Gunicorn..."
exec gunicorn -c gunicorn/gunicorn.conf.py ask_sharkevich.wsgi