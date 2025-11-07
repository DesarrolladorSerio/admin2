# ======== Etapa base ========
FROM nginx:1.25.5-alpine

LABEL maintainer="Augusto Fuenzalida" \
    version="1.0" \
    description="API Gateway con Nginx para Proyecto Redes 2025-II"

# Instalar wget para healthcheck
RUN apk add --no-cache wget

# Crear y ajustar permisos para directorios usados por Nginx
RUN mkdir -p /var/cache/nginx /var/run /var/log/nginx && \
    touch /var/run/nginx.pid && \
    chown -R nginx:nginx /var/cache/nginx /var/run /var/log/nginx /var/run/nginx.pid

# Copiar configuración personalizada
COPY nginx.conf /etc/nginx/nginx.conf

# Exponer puerto HTTP
EXPOSE 80

# Cambiar a usuario no root
USER nginx

# Iniciar Nginx
CMD ["nginx", "-g", "daemon off;"]

HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD wget -qO- http://localhost:80 || exit 1
