# Imagen base Python 3.11
FROM python:3.11.9-slim

LABEL maintainer="Augusto Fuenzalida <augusto@utalca.cl>" \
      version="1.0" \
      description="Microservicio FastAPI - notifications-service"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Copiar requirements e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copiar aplicación
COPY . .

# Crear usuario no-root y ajustar permisos
RUN useradd -m appuser && mkdir -p /app/logs /app/templates && chown -R appuser:appuser /app
USER appuser

ENV PORT=8004
EXPOSE ${PORT}

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD ["sh", "-c", "curl -f http://localhost:${PORT}/health || exit 1"]

# Comando de inicio (usar este container también para celery-worker; Compose override command for worker)
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
