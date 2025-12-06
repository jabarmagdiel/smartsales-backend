FROM python:3.15-rc-alpine3.22

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-railway.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8080
ENV FORCE_POSTGRESQL=true
ENV DJANGO_SETTINGS_MODULE=backend_salessmart.settings_production

EXPOSE 8080
RUN ln -s /usr/bin/python3 /usr/bin/python

CMD python3 manage.py migrate --settings=backend_salessmart.settings_production && \
    python3 manage.py collectstatic --noinput --settings=backend_salessmart.settings_production && \
    python3 create_admin.py && \
    daphne backend_salessmart.asgi:application --bind 0.0.0.0 --port $PORT

