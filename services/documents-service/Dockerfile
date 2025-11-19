FROM python:3.11.9-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements y instalar dependencias Python con reintentos
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip --timeout 300 --retries 3 \
  && (pip install --no-cache-dir -r requirements.txt --timeout 300 --retries 3 || \
      (echo "Retrying pip install with different settings..." && \
       pip install --no-cache-dir -r requirements.txt --timeout 600 --retries 5 --trusted-host pypi.org --trusted-host files.pythonhosted.org))

# Copiar código de la aplicación
COPY . .

# Crear directorio para almacenamiento
RUN mkdir -p /app/storage/documents/antiguos && chmod -R 777 /app/storage

# Exponer puerto
EXPOSE 8003

# Comando para iniciar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]
