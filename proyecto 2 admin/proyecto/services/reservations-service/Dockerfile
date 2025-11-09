# ======== Etapa de construcción ========
FROM python:3.11.9-slim

LABEL maintainer="Augusto Fuenzalida <augusto@utalca.cl>" \
      version="1.0" \
      description="Microservicio FastAPI - reservations-service"

WORKDIR /app

# Copiar requirements e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# instalar herramientas necesarias para healthcheck (curl)
RUN apt-get update \
  && apt-get install -y --no-install-recommends curl \
  && rm -rf /var/lib/apt/lists/*

# Copiar aplicación
COPY . .

# Crear usuario no-root y ajustar permisos
RUN useradd -m appuser && chown -R appuser /app
USER appuser

ENV PORT=8000
EXPOSE ${PORT}

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=5 \
  CMD ["sh", "-c", "curl -f http://localhost:${PORT}/health || exit 1"]

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
