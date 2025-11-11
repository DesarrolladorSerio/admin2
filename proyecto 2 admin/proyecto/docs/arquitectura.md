# Arquitectura

- Frontend: React + Vite + Tailwind CSS (Node 20.x base).
- Backend: FastAPI con Uvicorn (Python 3.11).
- DB: PostgreSQL 16.4.
- API Gateway: Nginx 1.25.x con rutas a frontend y backend.
- Docker Compose para orquestación.

## Alta disponibilidad (HA)

- La base de datos de `reservations` se ha separado en `reservations-db-primary` y `reservations-db-replica`.
- La réplica se inicializa mediante `pg_basebackup` desde la primaria; los parámetros de conexión se proporcionan mediante variables de entorno (PRIMARY_HOST, PRIMARY_PORT, REPLICATION_USER, REPLICATION_PASSWORD).
- Los servicios críticos (`auth-service` y `reservations-service`) tienen instancias duplicadas (`-1` y `-2`) y el `api-gateway` balancea entre ellas mediante upstreams en Nginx.

Nota: la configuración incluida está pensada para entornos de desarrollo y demostración. Para entornos productivos se recomienda una solución más robusta (Cluster manager, monitoreo y failover automático con herramientas dedicadas).
