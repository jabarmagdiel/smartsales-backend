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

# Copiar requirements primero
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código del backend
COPY . .

# Recopilar estáticos
RUN python manage.py collectstatic --noinput --settings=backend_salessmart.settings

# Exponer puerto requerido por Cloud Run
EXPOSE 8080

# Iniciar Gunicorn correctamente
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "backend_salessmart.wsgi:application"]
