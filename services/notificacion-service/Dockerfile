# ======== Stage 1: Builder ========
FROM python:3.11.9-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies to user directory
COPY requirements.txt .
RUN pip install --upgrade setuptools && pip install --user --no-cache-dir -r requirements.txt

# ======== Stage 2: Runtime ========
FROM python:3.11.9-slim

# Update OS and system python packages
RUN apt-get update && apt-get upgrade -y && \
    pip install --upgrade pip setuptools && \
    rm -rf /var/lib/apt/lists/*

LABEL maintainer="Augusto Fuenzalida <augusto@utalca.cl>" \
  version="1.0" \
  description="Microservicio FastAPI - notifications-service"

# Security: Run vulnerability scan with: trivy image <image-name>

ENV PYTHONUNBUFFERED=1 \
  PYTHONDONTWRITEBYTECODE=1 \
  PIP_NO_CACHE_DIR=1 \
  PIP_DISABLE_PIP_VERSION_CHECK=1 \
  MALLOC_ARENA_MAX=2 \
  PATH=/home/appuser/.local/bin:$PATH

WORKDIR /app

# Install runtime dependencies (curl for healthcheck)
RUN apt-get update \
  && apt-get upgrade -y \
  && apt-get install -y --no-install-recommends curl \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Create non-privileged user
RUN useradd --system --no-create-home appuser

# Copy dependencies from builder
COPY --from=builder /root/.local /home/appuser/.local

# Copy application code
COPY . .

# Create directories and set permissions
RUN mkdir -p /app/logs /app/templates \
    && chown -R appuser:appuser /app

# Switch to non-privileged user
USER appuser

ENV PORT=8004
EXPOSE ${PORT}

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD ["sh", "-c", "curl -f http://localhost:${PORT}/health || exit 1"]

# Command to start the application
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT} --workers 1 --loop asyncio"]
