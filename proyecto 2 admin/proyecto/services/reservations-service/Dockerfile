# ======== Etapa de construcción ========
FROM python:3.11.9-slim AS builder

LABEL maintainer="Augusto Fuenzalida" \
    version="1.0" \
    description="Backend FastAPI del Proyecto Redes 2025-II"

# Crear usuario no root
RUN adduser --disabled-password appuser

WORKDIR /app

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl && rm -rf /var/lib/apt/lists/*

# Copiar archivos de dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente
COPY . .

# Cambiar al usuario no root
USER appuser

# Exponer el puerto de FastAPI
EXPOSE 8000

# Comando de arranque
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
