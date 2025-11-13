FROM python:3.11-slim

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

EXPOSE 8080

CMD python manage.py migrate --settings=backend_salessmart.settings_railway && \
    python manage.py collectstatic --noinput --settings=backend_salessmart.settings_railway && \
    daphne backend_salessmart.asgi:application --bind 0.0.0.0 --port $PORT
