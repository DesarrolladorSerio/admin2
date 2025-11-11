## Stack de monitoreo (Prometheus / Grafana / Alertmanager)

Acceso
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001
  - Usuario admin: valor de `GRAFANA_ADMIN_USER` en el archivo `.env` (por defecto: `admin`)
  - Contraseña admin: valor de `GRAFANA_ADMIN_PASSWORD` en el archivo `.env`
- Alertmanager: http://localhost:9093

Enlaces rápidos
- Prometheus UI: http://localhost:9090
  - Targets: http://localhost:9090/targets
  - Rules: http://localhost:9090/rules
  - Alerts: http://localhost:9090/alerts
  - API (targets): http://localhost:9090/api/v1/targets
  - API (rules): http://localhost:9090/api/v1/rules
- Alertmanager UI: http://localhost:9093
  - API (alerts): http://localhost:9093/api/v2/alerts
- Grafana UI: http://localhost:3001
  - Dashboards: http://localhost:3001/dashboards
  - Datasources: http://localhost:3001/datasources

Exporters (métricas /metrics, accesibles en el host si los puertos están publicados):
- Node exporter: http://localhost:9100/metrics
- Redis exporter: http://localhost:9121/metrics
- Postgres exporter (auth): http://localhost:9187/metrics
- Postgres exporter (reservations): http://localhost:9188/metrics
- Postgres exporter (documents): http://localhost:9189/metrics

Otros enlaces útiles
- MinIO (S3): http://localhost:9000
- MinIO Console: http://localhost:9001

Nota: Si algunos endpoints devuelven errores de resolución DNS desde Prometheus, revisa que los servicios estén levantados y que formen parte de la misma red Docker (`monitoring_net` o `backend_net`).

Notas
- Las credenciales se guardan en el archivo de proyecto `.env` (ya está en `.gitignore`). NO subas `.env` al control de versiones.

Qué métricas se recogen
- `node_exporter` (job: `node_exporter`) — métricas del host/servidor (CPU, memoria, disco, carga).
- `postgres_exporters` (job: `postgres_exporters`) — métricas de PostgreSQL para las bases `auth`, `reservations` y `documents` (conexiones, lag de replicación, consultas, etc.).
- `redis_exporter` (job: `redis_exporter`) — métricas de Redis (keyspace, memoria, operaciones).
- Job `services` (job: `services`) — intenta scrapear `/metrics` en los servicios de la aplicación. Muchas instancias FastAPI no exponen `/metrics` por defecto (devuelven 404). Si instrumentas con la librería de Prometheus, aparecerán automáticamente.

Dashboards en Grafana
- `postgres_overview.json` — paneles de resumen para PostgreSQL (conexiones, consultas/s, estado de replicación, errores).
- `redis_metrics.json` — panel de Redis (memoria, operaciones, aciertos/fallos de keyspace).
- `containers_overview.json` — vista general de contenedores/hosts basada en `node_exporter` y los exporters.

Reglas de alerta (ruta: `infrastructure/monitoring/alert_rules.yml`)
- DBDown
  - Expresión: `up{job="postgres_exporters"} == 0`
  - Duración: 1m
  - Qué monitoriza: cualquier objetivo del job `postgres_exporters` que deje de responder. Genera una alerta `critical` por instancia afectada.

- RedisDown
  - Expresión: `up{job="redis_exporter"} == 0`
  - Duración: 1m
  - Qué monitoriza: el objetivo `redis_exporter` que deje de responder.

- HighCPU
  - Expresión (node_exporter):
    (1 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[2m])) / avg by (instance) (rate(node_cpu_seconds_total[2m])))) > 0.9
  - Duración: 2m
  - Qué monitoriza: hosts con uso de CPU sostenido superior al 90% (promediado) durante más de 2 minutos.

Cómo se enrutan las alertas
- Prometheus envía las alertas a Alertmanager (configurado en `alertmanager:9093`). La configuración actual de Alertmanager enruta las alertas al receptor `log` por simplicidad. Puedes configurar receptores de email, Slack, webhooks u otros en `infrastructure/monitoring/alertmanager.yml`.

Resolución de problemas
- Si observas muchas alertas `up == 0`, comprueba si los nombres de host de los targets son resolvibles desde dentro del contenedor de Prometheus. Los errores de DNS ("lookup <service> on 127.0.0.11:53: no such host") aparecen cuando los targets no están en la misma red Docker o los nombres de contenedor cambiaron.
- Para recargar la configuración de Prometheus sin reiniciar: `curl -X POST http://localhost:9090/-/reload`.
- Para recargar la configuración de Alertmanager: `curl -X POST http://localhost:9093/-/reload`.

Notas sobre Windows / cAdvisor
- `cAdvisor` fue eliminado de `docker-compose.yml` por incompatibilidades de cgroup/mount en Docker Desktop para Windows. Si necesitas métricas por contenedor, ejecuta cAdvisor en un host Linux o en WSL2.
