release: python manage.py migrate --noinput
web: gunicorn college_management_system.wsgi --workers 3 --timeout 120 --bind 0.0.0.0:${PORT:-8000}
