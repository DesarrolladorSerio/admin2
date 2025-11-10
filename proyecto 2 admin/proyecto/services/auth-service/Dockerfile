FROM python:3.11.9-slim

LABEL maintainer="Augusto Fuenzalida <augusto@utalca.cl>" \
  version="1.0" \
  description="Microservicio FastAPI - auth-service"

# Configurar variables de entorno para optimizar memoria
ENV PYTHONUNBUFFERED=1 \
  PYTHONDONTWRITEBYTECODE=1 \
  PIP_NO_CACHE_DIR=1 \
  PIP_DISABLE_PIP_VERSION_CHECK=1 \
  MALLOC_ARENA_MAX=2

WORKDIR /app

# Copiar requirements e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt \
  && find /usr/local -type d -name '__pycache__' -exec rm -rf {} + \
  && find /usr/local -type f -name '*.pyc' -delete

# instalar herramientas necesarias para healthcheck (curl)
RUN apt-get update \
  && apt-get install -y --no-install-recommends curl \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Copiar aplicación
COPY . .

# Crear usuario no-root y ajustar permisos
RUN useradd --system --no-create-home appuser && chown -R appuser /app
USER appuser

ENV PORT=8000
EXPOSE ${PORT}

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=5 \
  CMD ["sh", "-c", "curl -f http://localhost:${PORT}/health || exit 1"]

# Usar shell para permitir expansión de ${PORT} con optimizaciones
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT} --workers 1 --loop asyncio"]
