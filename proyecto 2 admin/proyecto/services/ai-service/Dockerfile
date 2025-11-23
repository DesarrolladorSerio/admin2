# ======== Etapa de construcción ========
FROM python:3.11-slim AS builder

WORKDIR /app

# Configurar variables de entorno para optimizar memoria
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    MALLOC_ARENA_MAX=2

# Copiar archivos de requisitos y crear wheels
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip --timeout 300 --retries 3 && \
    pip wheel --no-cache-dir -r requirements.txt -w /wheels --timeout 300 --retries 3

# ======== Etapa de ejecución ========
FROM python:3.11-slim

WORKDIR /app

# Configurar variables de entorno para optimizar memoria
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    MALLOC_ARENA_MAX=2

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Copiar wheels desde la etapa de construcción
COPY --from=builder /wheels /wheels

# Instalar dependencias de Python desde wheels
RUN pip install --no-cache-dir /wheels/* && \
    rm -rf /wheels && \
    find /usr/local -type d -name '__pycache__' -exec rm -rf {} + && \
    find /usr/local -type f -name '*.pyc' -delete

# Copiar código de la aplicación
COPY . .

# Crear usuario no-root para seguridad y menor uso de memoria
RUN adduser --system --no-create-home --disabled-login --group appuser && \
    groupadd -r appgroup && usermod -a -G appgroup appuser && \
    mkdir -p /app/models && chown -R appuser:appgroup /app/models

USER appuser

# Exponer puerto
EXPOSE 8005

# Comando para ejecutar la aplicación con optimizaciones de memoria
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8005", "--workers", "1", "--loop", "asyncio"]
