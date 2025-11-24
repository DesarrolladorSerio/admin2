# ======== Etapa de construcción ========
FROM python:3.11.9-slim AS builder

WORKDIR /app

# Instalar dependencias del sistema necesarias para compilar
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements y crear wheels
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip --timeout 300 --retries 3 && \
    pip wheel --no-cache-dir -r requirements.txt -w /wheels --timeout 300 --retries 3

# ======== Etapa de ejecución ========
FROM python:3.11.9-slim

WORKDIR /app

# Instalar curl para healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Copiar wheels desde la etapa de construcción
COPY --from=builder /wheels /wheels

# Instalar dependencias desde wheels
RUN pip install --no-cache-dir /wheels/* && \
    rm -rf /wheels && \
    find /usr/local -type d -name '__pycache__' -exec rm -rf {} + && \
    find /usr/local -type f -name '*.pyc' -delete

# Copiar código de la aplicación
COPY . .

# Crear usuario no‑root y directorio de almacenamiento con permisos seguros
RUN useradd --system --no-create-home appuser && \
    mkdir -p /app/storage/documents/antiguos && \
    chown -R appuser:appuser /app/storage && \
    chmod -R 750 /app/storage

# Cambiar a usuario no root
USER appuser

EXPOSE 8003

# Comando para iniciar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]
