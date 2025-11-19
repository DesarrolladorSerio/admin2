# Pruebas de Alta Disponibilidad (HA) y Replicación PostgreSQL

Este documento explica, paso a paso, cómo demostrar:
- Alta disponibilidad de los servicios detrás del API Gateway (Nginx) al “matar” una réplica.
- Replicación maestro–réplica (streaming) y un failover manual en PostgreSQL.

Todas las instrucciones están pensadas para Windows PowerShell.

---
## 0) Pre‑requisitos
- Stack levantado con `docker compose up -d`.
- Verifica rápidamente el estado:
  ```powershell
  docker compose ps
  ```
- El gateway está expuesto en el puerto 8081:
  ```powershell
  Write-Host "Gateway en http://localhost:8081"
  ```

---
## 1) Alta Disponibilidad de servicios (balanceo por Nginx)

Ejemplo con el servicio de Autenticación (2 réplicas: `auth-service-1` y `auth-service-2`). La misma lógica aplica al servicio de Reservas.

1. Comprobar salud por el gateway (repite 2–3 veces):
   ```powershell
   curl.exe "http://localhost:8081/api/auth/health"
   # Esperado: 200 OK (texto: OK u otro contenido breve)
   ```

2. "Matar" una réplica del servicio y comprobar continuidad:
   ```powershell
   docker compose stop auth-service-1
   curl.exe "http://localhost:8081/api/auth/health"   # Debe seguir 200 (atiende auth-service-2)
   ```

3. Recuperar la réplica caída:
   ```powershell
   docker compose start auth-service-1
   ```

4. Repetir con el clúster de Reservas:
   ```powershell
   curl.exe "http://localhost:8081/api/reservations/health"  # 200
   docker compose stop reservations-service-1
   curl.exe "http://localhost:8081/api/reservations/health"  # sigue 200 (atiende reservations-service-2)
   docker compose start reservations-service-1
   ```

Notas:
- Si detienes las DOS réplicas de un mismo servicio, el gateway responderá 502 (no hay backends disponibles): comportamiento esperado.
- Puedes mostrar en Prometheus → Targets que los exporters de infraestructura siguen `UP` aunque una instancia de app esté detenida.

---
## 2) Replicación PostgreSQL (maestro–réplica) y failover manual

Usaremos la base de autenticación: primario `auth-db` y réplica `auth-db-replica`.

1. Ver estado de la replicación en el primario:
   ```powershell
   docker compose exec auth-db psql -U admin -d auth_db -c "SELECT client_addr, state, sync_state FROM pg_stat_replication;"
   # Esperado: fila con state='streaming' y sync_state='async'
   ```

2. Confirmar que la réplica está en modo recuperación (standby):
   ```powershell
   docker compose exec auth-db-replica psql -U admin -d auth_db -c "SELECT pg_is_in_recovery();"
   # Esperado: t
   ```

3. Insertar datos en el primario y verificar que llegan a la réplica:
   ```powershell
   docker compose exec auth-db psql -U admin -d auth_db -c "CREATE TABLE IF NOT EXISTS test_rep(id SERIAL PRIMARY KEY, msg TEXT); INSERT INTO test_rep(msg) VALUES ('registro desde primario');"
   docker compose exec auth-db-replica psql -U admin -d auth_db -c "SELECT * FROM test_rep ORDER BY id DESC LIMIT 3;"
   # Esperado: se ve el registro insertado
   ```

4. Simular caída del primario y promover la réplica (failover manual):
   ```powershell
   docker compose stop auth-db
   docker compose exec auth-db-replica bash -lc "su postgres -c '/usr/lib/postgresql/16/bin/pg_ctl -D /var/lib/postgresql/data promote'"
   docker compose exec auth-db-replica psql -U admin -d auth_db -c "SELECT pg_is_in_recovery();"    # Esperado: f
   ```

## 5) Backups manuales y restauración (añadido)

### 5.1 Ejecutar un backup inmediato (one‑off)
Genera los dumps de las 3 bases y lista los archivos creados en el volumen `/backups`.

```powershell
docker compose run --rm -e BACKUP_ONCE=1 pg-backup /bin/sh -c "/app/backup.sh && ls -l /backups"
```

Esperado:
- `backup_auth_YYYY-MM-DD.sql`
- `backup_res_YYYY-MM-DD.sql`
- `backup_doc_YYYY-MM-DD.sql`
- Mensajes de subida a MinIO si `MINIO_BUCKET` está configurado (por defecto `db-backups`).

---
## 6) Enlaces rápidos de monitoreo

Para agilizar la demostración y ver estados / alertas sin navegar manualmente:

### Prometheus
- UI principal: http://localhost:9090/
- Targets (ver qué está UP/DOWN): http://localhost:9090/targets
- Query “up” pre‑cargada: http://localhost:9090/graph?g0.expr=up&g0.tab=0
- Alertas activas: http://localhost:9090/alerts

### Alertmanager
- Estado y alertas enrutadas: http://localhost:9093/#/alerts
- Config / silences: http://localhost:9093/#/silences

### Grafana
- Login: http://localhost:3001/ (usuario `${GRAFANA_ADMIN_USER}`, contraseña `${GRAFANA_ADMIN_PASSWORD}` definidas en `.env`)
- Dashboards (carpeta “General”): http://localhost:3001/dashboards
- Explorador de métricas (Prometheus): http://localhost:3001/explore

### Exporters individuales (útil para debug directo)
- Node Exporter: http://localhost:9100/metrics
- Redis Exporter: http://localhost:9121/metrics
- Postgres Auth: http://localhost:9187/metrics
- Postgres Reservas: http://localhost:9188/metrics
- Postgres Documentos: http://localhost:9189/metrics
 

### Servicios de infraestructura
- MinIO Console: http://localhost:9001/ (usuario: `${MINIO_ACCESS_KEY}`, contraseña: `${MINIO_SECRET_KEY}`)
- MinIO API: http://localhost:9000/
 

### Bases de datos (puertos expuestos)
- Auth DB (Primary): localhost:5432
- Reservations DB (Primary): localhost:5433
- Documents DB: localhost:5434
 

### Frontend y Gateway
- Frontend (React): http://localhost:3000/
- API Gateway (Nginx): http://localhost:8081/

Notas:
- cAdvisor está omitido en Windows (limitaciones cgroup); para métricas de contenedores usar Linux/WSL2 si se requiere.
- Las aplicaciones FastAPI no exponen aún `/metrics`; por eso aparecerán como DOWN en Prometheus si se configuró algún job hacia ellas. No afecta la demo de HA ni la de replicación.

Fin de la guía.

