# Informe Técnico: Implementación de Hardening en Contenedores

**Estudiante:** Augusto Fuenzalida
**Fecha:** 25 de Noviembre de 2025
**Asignatura:** Administración de Redes / Seguridad en Sistemas
**Referencia:** Laboratorio - Proyecto Admin 3

---

## 1. Objetivo de la Actividad
El propósito de esta práctica fue implementar técnicas de *hardening* (endurecimiento) en los contenedores Docker del proyecto "Admin 3", enfocándose en la reducción de privilegios, la minimización del tamaño de las imágenes y la limitación de recursos del sistema.

## 2. Desarrollo de la Implementación

### 2.1. Optimización de Dockerfiles (Multi-stage Builds)
Se refactorizaron los archivos `Dockerfile` monolíticos para utilizar construcciones en múltiples etapas (*multi-stage builds*). Esto permitió separar las herramientas de compilación (como `gcc`) del entorno de ejecución final.

**Comparativa de Código:**

*Configuración Insegura (Antes):*
Se utilizaba una imagen base estándar y se ejecutaba la aplicación con el usuario `root` por defecto.

```dockerfile
FROM python:3.11
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "main.py"]
```

*Configuración Endurecida (Implementación Actual - `services/auth-service`):*
Se implementó un usuario no privilegiado (`appuser`) y se limpiaron los cachés de instalación.

```dockerfile
# Etapa 1: Builder
FROM python:3.11.9-slim AS builder
WORKDIR /app
RUN apt-get update && apt-get install -y gcc ...
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Etapa 2: Runtime
FROM python:3.11.9-slim
# Actualización de seguridad del SO base
RUN apt-get update && apt-get upgrade -y
# Creación de usuario de sistema sin home
RUN useradd --system --no-create-home appuser
COPY --from=builder /root/.local /home/appuser/.local
WORKDIR /app
USER appuser
```

**Impacto en el Tamaño de Imágenes:**
El uso de multi-stage builds redujo significativamente el tamaño de las imágenes, disminuyendo la superficie de ataque al eliminar binarios innecesarios.

- **Auth Service:** Reducción de ~900MB a ~200MB (~78% de optimización).
- **Frontend:** Reducción de ~1.2GB a ~40MB mediante el uso de Nginx Alpine (~96% de optimización).

### 2.2. Políticas de Seguridad en Docker Compose
Para garantizar la consistencia en todos los servicios, se definieron anclas YAML (`x-security`) en el archivo `docker-compose.yml`. Esto permite aplicar restricciones de kernel y recursos de manera global.

```yaml
x-security: &security
  security_opt:
    - no-new-privileges:true
  cap_drop:
    - ALL
  deploy:
    resources:
      limits:
        cpus: "0.5"
        memory: 512M
```

## 3. Justificación Técnica de las Medidas

### 3.1. Usuarios No Privilegiados (non-root)
La ejecución de procesos como root dentro de un contenedor aumenta el riesgo de "Container Breakout". Si un atacante logra explotar una vulnerabilidad en la aplicación, podría obtener privilegios elevados en el host. Para mitigar esto, se crearon usuarios específicos (`appuser`, `nginx`, `minio`) en todos los servicios.

### 3.2. Eliminación de Capacidades (Linux Capabilities)
Por defecto, Docker otorga capacidades del kernel que no son necesarias para aplicaciones web estándar. Se aplicó la directiva `cap_drop: ALL` para eliminar todos los privilegios, añadiendo posteriormente solo las excepciones estrictamente necesarias (como `CHOWN` o `SETUID` para bases de datos PostgreSQL).

### 3.3. Mitigación de Vulnerabilidades (CVEs)
Se adoptaron dos estrategias principales:
1. **Fijación de Versiones:** Uso de tags específicos (ej. `python:3.11.9-slim`) para asegurar la reproducibilidad y evitar cambios disruptivos.
2. **Actualización Base:** Inclusión de comandos `apk upgrade` o `apt-get upgrade` en la fase de construcción para parchar vulnerabilidades conocidas del sistema operativo base.

## 4. Detalle por Servicio

- **Backend (Python):** Se eliminó el acceso a shell de login para el usuario `appuser`.
- **Frontend (Nginx):** Se restringieron los permisos de escritura, permitiendo acceso únicamente a `/var/cache/nginx` y `/var/run`.
- **MinIO (S3):** Se realizó una migración mayor desde una imagen basada en RedHat a una personalizada en Alpine, copiando binarios estáticos para eliminar vulnerabilidades de librerías del sistema.

