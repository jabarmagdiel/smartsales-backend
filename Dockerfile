# Imagen base
FROM python:3.11-slim

# Configuración básica
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar dependencias
COPY requirements-railway.txt requirements.txt

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el proyecto
COPY . .

# Recoger archivos estáticos
RUN python manage.py collectstatic --noinput --settings=backend_salessmart.settings_railway

# Cloud Run necesita que la app escuche en $PORT (por defecto 8080)
ENV PORT=8080

# Exponer el puerto (opcional)
EXPOSE 8080

# Comando de ejecución con Gunicorn
CMD exec gunicorn backend_salessmart.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 2 \
    --threads 4 \
    --timeout 0
