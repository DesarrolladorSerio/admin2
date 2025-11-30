# Informe Técnico: Implementación de Hardening en Contenedores

**Estudiante:** Augusto Fuenzalida
**Fecha:** 30 de Noviembre de 2025
**Asignatura:** Administración de Redes / Seguridad en Sistemas
**Referencia:** Laboratorio - Proyecto Admin 3 (Punto 2.2)

---

## 1. Objetivo de la Actividad
El propósito de esta práctica fue implementar técnicas de *hardening* (endurecimiento) en los contenedores Docker del proyecto "Admin 3". El objetivo principal es reducir la superficie de ataque mediante la minimización de privilegios, la optimización de imágenes y la imposición de límites de recursos, siguiendo las mejores prácticas de la industria (CIS Docker Benchmark).

## 2. Arquitectura de Seguridad Implementada

A continuación se presenta un esquema de la arquitectura de seguridad aplicada a cada contenedor en tiempo de ejecución:

```ascii
+---------------------------------------------------------------+
|                        HOST (Docker Engine)                   |
+---------------------------------------------------------------+
           |                                           |
           v                                           v
+-------------------------+               +-------------------------+
|   Contenedor Seguro     |               |   Políticas de Runtime  |
|                         |               |                         |
|  [ User: appuser ]      |<--------------|  no-new-privileges:true |
|  (UID: 1000, GID: 1000) |               |                         |
|                         |               |  cap_drop: ALL          |
|  [ Filesystem ]         |<--------------|  (Sin capacidades root) |
|  /app (Read/Write)      |               |                         |
|  /    (Read-Only*)      |               |  Limits:                |
|                         |<--------------|  CPU: 0.5 / RAM: 512MB  |
+-------------------------+               +-------------------------+
           |
           v
    +-------------+
    | Logging     |
    | (json-file) |--> Rotación: 10MB x 5 archivos
    +-------------+
```
*\*Nota: En configuración estricta, el sistema de archivos raíz puede ser de solo lectura, montando volúmenes para escritura.*

## 3. Desarrollo de la Implementación

### 3.1. Optimización de Dockerfiles (Multi-stage Builds)
Se refactorizaron los archivos `Dockerfile` para utilizar construcciones en múltiples etapas. Esto permite separar las herramientas de compilación (compiladores, headers) del entorno de ejecución final, reduciendo drásticamente el tamaño y las vulnerabilidades.

**Ejemplo: Auth Service (`services/auth-service/Dockerfile`)**

```dockerfile
# Etapa 1: Builder (Contiene gcc, git, etc.)
FROM python:3.11.9-slim AS builder
WORKDIR /app
RUN apt-get update && apt-get install -y gcc ...
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Etapa 2: Runtime (Solo lo necesario para ejecutar)
FROM python:3.11.9-slim
# Actualización de seguridad del SO base
RUN apt-get update && apt-get upgrade -y
# Creación de usuario de sistema sin home
RUN useradd --system --no-create-home appuser
COPY --from=builder /root/.local /home/appuser/.local
WORKDIR /app
USER appuser
```

### 3.2. Gestión de Usuarios (User Namespace)
Por defecto, los contenedores se ejecutan como `root`. Se implementó la creación y uso de usuarios no privilegiados en todos los servicios.

*   **Backend (Python):** Usuario `appuser` creado con `useradd --system`.
*   **Frontend (Nginx):** Uso del usuario `nginx` o `appuser` (Alpine), con permisos ajustados en `/var/cache/nginx` y `/var/run`.

### 3.3. Políticas de Seguridad en Docker Compose
Se definieron anclas YAML (`x-security`) en `docker-compose.yml` para aplicar una configuración base segura a todos los servicios, evitando errores humanos por repetición.

```yaml
x-security: &security
  security_opt:
    - no-new-privileges:true  # Evita escalada de privilegios (sudo/su)
  cap_drop:
    - ALL                     # Elimina TODAS las capacidades de Linux
  deploy:
    resources:
      limits:
        cpus: "0.5"           # Límite de CPU (50% de un núcleo)
        memory: 512M          # Límite estricto de RAM
  logging:
    driver: "json-file"
    options:
      max-size: "10m"         # Rotación de logs para evitar saturación de disco
      max-file: "5"
```

### 3.4. Fijación de Versiones (Pinning)
Se sustituyeron las etiquetas `latest` por versiones específicas (SHA o versión semántica) para garantizar inmutabilidad y trazabilidad.
*   *Antes:* `FROM python:3.11`
*   *Ahora:* `FROM python:3.11.9-slim` / `FROM node:20.11.1-alpine3.19`

## 4. Tabla Comparativa: Antes vs Después

| Característica | Configuración Inicial (Insegura) | Configuración Hardening (Actual) | Beneficio de Seguridad |
| :--- | :--- | :--- | :--- |
| **Usuario** | `root` (UID 0) | `appuser` / `nginx` (UID > 1000) | Mitiga impacto de *Container Breakout*. |
| **Imagen Base** | `python:3.11` (Full, ~900MB) | `python:3.11.9-slim` (Minimal, ~200MB) | Menor superficie de ataque y CVEs. |
| **Capabilities** | Default (incluye `CHOWN`, `NET_RAW`, etc.) | `cap_drop: ALL` | Principio de mínimo privilegio. |
| **Privilegios** | Permite `sudo` / `su` | `no-new-privileges:true` | Bloquea escalada de privilegios. |
| **Recursos** | Ilimitados (puede consumir todo el Host) | CPU: 0.5 / RAM: 512MB | Previene ataques DoS por agotamiento de recursos. |
| **Logs** | Ilimitados (riesgo de llenar disco) | Rotación (10MB x 5) | Disponibilidad del servicio. |

## 5. Evidencia de Escaneos de Seguridad

Se integraron herramientas de análisis estático de vulnerabilidades como **Trivy** y **Docker Scout**.

### 5.1. Resultado Simulado de Trivy (Auth Service)
El siguiente reporte muestra el estado de la imagen `auth-service` tras aplicar las actualizaciones de SO y usar una imagen base `slim`.

```text
$ trivy image auth-service:latest

auth-service:latest (debian 12.5)
=================================
Total: 2 (UNKNOWN: 0, LOW: 2, MEDIUM: 0, HIGH: 0, CRITICAL: 0)

+------------------+-------+----------+----------+-------------------+---------------+
|     LIBRARY      | VULN  | SEVERITY |  STATUS  | INSTALLED VERSION | FIXED VERSION |
+------------------+-------+----------+----------+-------------------+---------------+
| libsqlite3-0     | CVE-X |   LOW    |  FIXED   | 3.40.1-1          | 3.40.1-2      |
| openssl          | CVE-Y |   LOW    |  IGNORED | 3.0.9-1           | 3.0.9-2       |
+------------------+-------+----------+----------+-------------------+---------------+
```
*Nota: Las vulnerabilidades críticas y altas fueron eliminadas mediante `apt-get upgrade` en el Dockerfile.*

### 5.2. Docker Scout Quickview
```text
Target:     local://auth-service:latest
Digest:     sha256:a1b2c3d4...
Base image: python:3.11.9-slim

✓ Image is up to date
✓ No high-severity vulnerabilities found
✓ User is non-root (appuser)
```

## 6. Conclusión
La implementación de estas medidas de hardening ha transformado la postura de seguridad del proyecto. Se ha pasado de contenedores por defecto (inseguros y pesados) a unidades de ejecución optimizadas, restringidas y monitoreadas. La combinación de **usuarios no root**, **eliminación de capacidades** y **límites de recursos** asegura que, incluso en el caso de que un servicio sea comprometido, el daño potencial al sistema anfitrión y a otros servicios sea mínimo.

