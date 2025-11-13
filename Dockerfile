FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el proyecto
COPY . .

# Archivos estáticos
RUN python manage.py collectstatic --noinput

# Cloud Run usa el puerto dinámico $PORT
ENV PORT=8080
EXPOSE 8080

# Comando final
CMD exec gunicorn backend_salessmart.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 3 \
    --threads 2 \
    --timeout 0
