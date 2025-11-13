# Usar imagen base de Python
FROM python:3.11-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Copiar requirements primero para aprovechar cache de Docker
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY . .

# Recopilar archivos estáticos
RUN python manage.py collectstatic --noinput --settings=backend_salessmart.settings

# Crear usuario no-root para seguridad
RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
USER app

# Exponer puerto 8080 (requerido por Cloud Run)
EXPOSE 8080

# Comando para ejecutar la aplicación
CMD exec gunicorn --bind 0.0.0.0:8080 --workers 1 --threads 8 --timeout 0 backend_salessmart.wsgi:application
