# Proyecto

Estructura base con frontend (React + Vite + Tailwind), backend (FastAPI) y base de datos (PostgreSQL).

## Arranque rápido
1. Copia `.env.example` a `.env` y ajusta variables.
2. Construye e inicia: `docker-compose up -d --build`
3. Frontend: http://localhost:5173
4. API: http://localhost:8000
5. API vía gateway: http://localhost:8080/api
6. Base de datos expuesta en localhost:5432

## Alta disponibilidad (HA) - pruebas simples

Se ha añadido una configuración básica de alta disponibilidad para la base de datos de reservas y duplicación de servicios críticos.

- reservations-db-primary: instancia primaria de Postgres 16.4.
- reservations-db-replica: réplica en streaming (se inicializa mediante `pg_basebackup` desde la primaria).
- auth-service-1 / auth-service-2: instancias duplicadas del servicio de autenticación.
- reservations-service-1 / reservations-service-2: instancias duplicadas del servicio de reservas.

Prueba básica de failover (demostración):

1. Arranca el stack: `docker compose up -d --build`
2. Comprueba que las instancias están saludables: `docker compose ps`
3. Para simular una caída de la primaria de reservas, ejecuta:

```powershell
docker stop reservations_db_primary
```

4. La réplica (`reservations_db_replica`) permanecerá operativa como copia de solo lectura. Para promoverla a primaria deberás realizar pasos manuales de promoción (no automatizados aquí):

```powershell
docker exec -it reservations_db_replica bash
# Dentro del contenedor ejecutar: pg_ctl promote -D /var/lib/postgresql/data
```

5. Después de la promoción, actualiza las conexiones o recrea servicios si necesitas que apunten a la nueva primaria.

Notas:
- Esta configuración sirve para demostración y entornos de desarrollo. En producción se recomienda usar herramientas dedicadas (Patroni, repmgr) y un gestor de VIPs o proxy (pgpool, HAProxy) para conmutación automática.
