# Dashboards provisioning

Esta carpeta contiene los dashboards que Grafana cargará automáticamente en la carpeta "General" al iniciar.

Archivos incluidos (placeholders):

- `1860-node-exporter-full.json` — Node Exporter Full (CPU, RAM, disco)
- `9628-postgresql-overview.json` — PostgreSQL Overview
- `763-redis-dashboard.json` — Redis Dashboard
- `3662-prometheus-stats.json` — Prometheus Stats
- `12019-docker-and-system-monitoring.json` — Docker and System Monitoring (usa cAdvisor)
- `11074-alertmanager-overview.json` — Alertmanager Overview

Descarga automática (si tu entorno tiene acceso a internet):

PowerShell (Windows):

```powershell
# Ejecutar desde esta carpeta
Invoke-WebRequest -UseBasicParsing -OutFile 1860-node-exporter-full.json https://grafana.com/api/dashboards/1860/revisions/latest/download
Invoke-WebRequest -UseBasicParsing -OutFile 9628-postgresql-overview.json https://grafana.com/api/dashboards/9628/revisions/latest/download
Invoke-WebRequest -UseBasicParsing -OutFile 763-redis-dashboard.json https://grafana.com/api/dashboards/763/revisions/latest/download
Invoke-WebRequest -UseBasicParsing -OutFile 3662-prometheus-stats.json https://grafana.com/api/dashboards/3662/revisions/latest/download
Invoke-WebRequest -UseBasicParsing -OutFile 12019-docker-and-system-monitoring.json https://grafana.com/api/dashboards/12019/revisions/latest/download
Invoke-WebRequest -UseBasicParsing -OutFile 11074-alertmanager-overview.json https://grafana.com/api/dashboards/11074/revisions/latest/download
```

Bash/curl:

```bash
curl -L -o 1860-node-exporter-full.json https://grafana.com/api/dashboards/1860/revisions/latest/download
curl -L -o 9628-postgresql-overview.json https://grafana.com/api/dashboards/9628/revisions/latest/download
curl -L -o 763-redis-dashboard.json https://grafana.com/api/dashboards/763/revisions/latest/download
curl -L -o 3662-prometheus-stats.json https://grafana.com/api/dashboards/3662/revisions/latest/download
curl -L -o 12019-docker-and-system-monitoring.json https://grafana.com/api/dashboards/12019/revisions/latest/download
curl -L -o 11074-alertmanager-overview.json https://grafana.com/api/dashboards/11074/revisions/latest/download
```

Después de descargar los JSON reales, reinicia Grafana para que los cargue:

```powershell
docker compose restart grafana
```

Nota importante sobre Docker Containers Overview:

El dashboard `12019 - Docker and System Monitoring` usa métricas expuestas por cAdvisor para listar métricas y detalles de contenedores. En Windows cAdvisor suele fallar por restricciones de cgroups/paths; si tu entorno es Docker Desktop en Windows es probable que el panel de contenedores quede vacío. Si quieres métricas de contenedores en Windows, considera ejecutar cAdvisor en un host Linux o usar métricas del propio Docker Engine si las expones a Prometheus.
