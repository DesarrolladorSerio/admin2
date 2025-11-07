# ======== Etapa de construcción ========
FROM node:20.11.1-alpine3.19 AS builder

LABEL maintainer="Augusto Fuenzalida" \
      version="1.0" \
      description="Frontend React + Vite + Tailwind para Proyecto Redes 2025-II"

WORKDIR /app

# Crear usuario no root
RUN adduser -D appuser

# Copiar e instalar dependencias
COPY package.json package-lock.json* ./
RUN npm install

# Copiar el resto del código y construir
COPY . .
RUN npm run build

# ======== Etapa de despliegue ========
FROM nginx:1.25.5-alpine

LABEL maintainer="Augusto Fuenzalida" \
      version="1.0" \
      description="Frontend compilado servido con Nginx"

# Instalar wget para healthcheck
RUN apk add --no-cache wget

# Crear y dar permisos a directorios usados por Nginx
RUN mkdir -p /var/cache/nginx /var/run /var/log/nginx && \
      touch /var/run/nginx.pid && \
      chown -R nginx:nginx /var/cache/nginx /var/run /var/log/nginx /var/run/nginx.pid

# Copiar configuración de Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copiar los archivos compilados
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

# Cambiar a usuario no root (seguro)
USER nginx

# Iniciar nginx
CMD ["nginx", "-g", "daemon off;"]

HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD wget -qO- http://localhost:80 || exit 1
