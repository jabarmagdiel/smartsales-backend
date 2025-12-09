release: python manage.py migrate --settings=backend_salessmart.settings_railway && python manage.py collectstatic --noinput --settings=backend_salessmart.settings_railway
web: gunicorn backend_salessmart.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --log-level info
