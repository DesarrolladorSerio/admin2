# Testeos - Comprobaciones realizadas

Este documento recoge los pasos de prueba ("testeos") que ejecuté en el proyecto para verificar el API Gateway (Nginx), la copia de seguridad automática (pg-backup) y las respuestas ante fallos de backend. Incluye los comandos usados y los echos (salidas) importantes obtenidos durante la sesión.

> Archivos modificados / añadidos relacionados:
> - `services/api-gateway/nginx.conf`  (configuración del gateway: upstreams, timeouts, headers, /status y /health, error_page)
> - `services/api-gateway/Dockerfile`  (healthcheck apuntando a `/health`, copia de `50x.html`)
> - `services/api-gateway/50x.html`    (página genérica 50x)
> - `TESTEOS.md`                       (este fichero)

---

## 1) Prueba: backup manual (one-off)

Objetivo: ejecutar un backup manual con el servicio `pg-backup` y listar los archivos generados en `/backups`.

Comando ejecutado (PowerShell):

```powershell
docker compose run --rm -e BACKUP_ONCE=1 pg-backup /bin/sh -c "/app/backup.sh && ls -l /backups"
```

Echos importantes (recortado):

```
[entrypoint] Running one-off backup
[backup] Dumping auth_db from auth-db to /backups/backup_auth_2025-11-09.sql
[backup] Dumping reservations_db from reservations-db-primary to /backups/backup_res_2025-11-09.sql
[backup] Dumping documents_db from documents-db to /backups/backup_doc_2025-11-09.sql
[backup] Applying retention: keep last 7 days
[backup] Uploading backups to MinIO bucket: db-backups
..._2025-11-09.sql: 7.91 KiB / 7.91 KiB ┃▓▓▓▓...┃ 460.25 KiB/s 0s
[backup] Done at 2025-11-09T02:25:43+00:00
```

Resultado esperado/verificado:
- Se crearon tres archivos en `/backups`:
  - `backup_auth_2025-11-09.sql`
  - `backup_res_2025-11-09.sql`
  - `backup_doc_2025-11-09.sql`
- Los archivos fueron subidos al bucket `db-backups` de MinIO (si está configurado).

---

## 2) Prueba: endpoints del API Gateway (`/status` y `/health`)

Objetivo: comprobar que el gateway responde correctamente y que Docker healthcheck puede usar `/health`.

Comandos ejecutados (PowerShell):

```powershell
# reconstruir y arrancar el servicio gateway
docker compose build gateway
docker compose up -d gateway
Start-Sleep -Seconds 3

# probar endpoints
curl.exe -sS http://localhost/status
curl.exe -sS http://localhost/health
```

Echos (capturados):

```
--- /status ---
{"status":"ok","service":"api-gateway"}
--- /health ---
OK
HTTP_CODE:OK
```

Interpretación:
- `/status` devuelve JSON con {"status":"ok","service":"api-gateway"}.
- `/health` devuelve `OK` (texto) y código HTTP 200. El `HEALTHCHECK` de la imagen fue actualizado para usar `/health`.

---

## 3) Prueba: simulación de fallo de backend (auth) y ver `50x.html`

Objetivo: forzar que ambos backends de `auth` estén caídos y comprobar que Nginx devuelve la página genérica 50x (error_page 502).

Pasos ejecutados (PowerShell):

```powershell
# Parar instancias de auth
docker compose stop auth-service-1 auth-service-2
Start-Sleep -Seconds 2

# Solicitar la ruta proxied
curl.exe -i -sS http://localhost/api/auth/

# Reiniciar las instancias de auth
docker compose start auth-service-1 auth-service-2
Start-Sleep -Seconds 3
```

Salida (capturada):

```
HTTP/1.1 502 Bad Gateway
Server: nginx/1.25.5
Date: Sun, 09 Nov 2025 13:52:29 GMT
Content-Type: text/html
Content-Length: 844
Connection: keep-alive
ETag: "69109acb-34c"
X-Frame-Options: SAMEORIGIN
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Content-Security-Policy: default-src 'self' 'unsafe-inline' data:;

<!doctype html>
<html lang="es">
... (contenido de 50x.html) ...
</html>
```

Interpretación:
- Cuando los backends `auth-service-1` y `auth-service-2` no responden, Nginx devuelve 502 junto con la página `50x.html`.
- Las cabeceras de seguridad añadidas en la configuración están presentes en la respuesta.

---

## 4) Comandos útiles (resumen para repetir las pruebas)

- Backup one-off (local):
```powershell
docker compose run --rm -e BACKUP_ONCE=1 pg-backup /bin/sh -c "/app/backup.sh && ls -l /backups"
```

- Reconstruir y arrancar gateway:
```powershell
docker compose build gateway
docker compose up -d gateway
```

- Probar endpoints del gateway:
```powershell
curl.exe -sS http://localhost/status
curl.exe -sS http://localhost/health
```

- Forzar 502 (simulación) y ver la página 50x (NO ejecutar en producción sin coordinar):
```powershell
# Parar servicios auth
docker compose stop auth-service-1 auth-service-2
# Hacer una petición
curl.exe -i -sS http://localhost/api/auth/
# Volver a levantar
docker compose start auth-service-1 auth-service-2
```

- Ver estado health del contenedor gateway:
```powershell
docker inspect --format='{{json .State.Health}}' proyecto_gateway
```

---

## 5) Notas y recomendaciones

- El gateway utiliza balanceo round-robin por defecto (múltiples `server` en `upstream`), y se añadieron timeouts y `proxy_next_upstream` para reducir errores transitorios.
- `50x.html` está marcada como `internal` (se sirve solo cuando Nginx invoca `error_page`). Si prefieres poder acceder directamente a `/50x.html`, quitar la directiva `internal` en `nginx.conf`.
- Si quieres evitar la subida a MinIO durante pruebas, deja `MINIO_BUCKET=` vacío en `.env` o ejecuta la variable de entorno `-e MINIO_BUCKET=` en la prueba del backup one-off.

---

Si quieres, puedo:
- Añadir una pequeña prueba automatizada (PowerShell script) que ejecute las comprobaciones y valide códigos HTTP y presencia de archivos de backup.
- Ampliar `TESTEOS.md` con logs completos (si prefieres mantener todo el dump de salida) o con resultados año/mes/día dinámicos.

Fin de `TESTEOS.md`.
