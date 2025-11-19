# Imagen base Python 3.11 optimizada
FROM python:3.11.9-slim

LABEL maintainer="Augusto Fuenzalida <augusto@utalca.cl>" \
  version="1.0" \
  description="Microservicio FastAPI - notifications-service"

ENV PYTHONUNBUFFERED=1 \
  PYTHONDONTWRITEBYTECODE=1 \
  PIP_NO_CACHE_DIR=1 \
  PIP_DISABLE_PIP_VERSION_CHECK=1 \
  MALLOC_ARENA_MAX=2

WORKDIR /app

# Instalar curl para healthcheck
RUN apt-get update \
  && apt-get install -y --no-install-recommends curl \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Copiar requirements e instalar dependencias con reintentos
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip --timeout 300 --retries 3 \
  && (pip install --no-cache-dir -r requirements.txt --timeout 300 --retries 3 || \
      (echo "Retrying pip install with different settings..." && \
       pip install --no-cache-dir -r requirements.txt --timeout 600 --retries 5 --trusted-host pypi.org --trusted-host files.pythonhosted.org)) \
  && find /usr/local -type d -name '__pycache__' -exec rm -rf {} + \
  && find /usr/local -type f -name '*.pyc' -delete

# Copiar aplicación
COPY . .

# Crear usuario no-root y ajustar permisos
RUN useradd --system --no-create-home appuser && mkdir -p /app/logs /app/templates && chown -R appuser:appuser /app
USER appuser

ENV PORT=8004
EXPOSE ${PORT}

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD ["sh", "-c", "curl -f http://localhost:${PORT}/health || exit 1"]

# Comando de inicio optimizado (usar este container también para celery-worker; Compose override command for worker)
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT} --workers 1 --loop asyncio"]
