# Hardening de Bases de Datos - Proyecto Admin 3

**Fecha:** 29 de Noviembre de 2025
**Referencia:** Seguridad en Bases de Datos y Redes

---

## 1. Medidas de Seguridad Implementadas

### 1.1. Autenticación Segura
- **Mecanismo:** Se ha configurado PostgreSQL para utilizar `scram-sha-256` como método de encriptación de contraseñas, reemplazando al obsoleto `md5`.
- **Contraseñas Fuertes:** Se han generado contraseñas aleatorias de alta entropía (>12 caracteres) para el usuario administrador y el usuario de aplicación.
- **Docker Secrets:** Las contraseñas ya no se pasan como texto plano en variables de entorno. Se utilizan **Docker Secrets** (`/run/secrets/db_password`) para inyectarlas de forma segura en el contenedor de base de datos.

### 1.2. Principio de Privilegio Mínimo
- **Usuario de Aplicación:** Se ha creado un usuario dedicado `app_user` para los microservicios.
- **Permisos Restringidos:** Este usuario tiene permisos limitados únicamente a `SELECT`, `INSERT`, `UPDATE` y `DELETE` sobre el esquema `public`.
- **Revocación:** Se han revocado todos los permisos administrativos (`DROP`, `ALTER`, `CREATE`) y el acceso por defecto al esquema `public`.
- **Uso Exclusivo:** Los microservicios ya no usan el usuario postgres, solo app_user con privilegios mínimos.

### 1.3. Aislamiento de Red
- **Red Interna:** Se ha creado una red Docker dedicada `backend-network` configurada como `internal: true`. Esto aísla completamente el tráfico de base de datos de internet y de la red pública.
- **Exposición de Puertos:** Se han eliminado las directivas `ports` de los servicios de base de datos (`auth-db`, `reservations-db`, `documents-db`, `redis`) en `docker-compose.yml`. Las bases de datos **NO** son accesibles desde el host ni desde redes externas.
- **Segmentación:** Solo los microservicios de backend tienen acceso a la red de base de datos. El API Gateway y el Frontend están aislados de esta red.

### 1.4. Logging y Auditoría
- **Configuración:** Se ha habilitado el registro detallado de conexiones y desconexiones en `postgresql.conf`.
- **Prefijo de Log:** Se configuró `log_line_prefix` para incluir timestamp, ID de proceso, usuario y base de datos, facilitando la trazabilidad.

### 1.5. Control de Acceso a Red (pg_hba.conf)
- **Restricción de Hosts:** Se ha configurado `pg_hba.conf` para rechazar explícitamente cualquier conexión que no provenga de las subredes internas de Docker (`172.16.0.0/12`, etc.).

**Configuración aplicada (`pg_hba.conf`):**
```conf
# TYPE  DATABASE        USER            ADDRESS                 METHOD
# Permitir conexiones desde la red interna de Docker
host    all             all             172.16.0.0/12           scram-sha-256
# Rechazar explícitamente todo lo demás
host    all             all             0.0.0.0/0               reject
```

---

## 2. Scripts y Archivos de Configuración

### 2.1. Script de Inicialización de Permisos
Ubicación: `infrastructure/database/init/01-app-permissions.sql`

```sql
-- Crea el usuario de aplicación
CREATE USER app_user WITH PASSWORD '...';

-- Revoca permisos por defecto
REVOKE ALL ON SCHEMA public FROM public;
REVOKE ALL ON SCHEMA public FROM app_user;

-- Otorga solo lo necesario
GRANT USAGE ON SCHEMA public TO app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;
```

### 2.2. Configuración de Postgres
Ubicación: `infrastructure/database/postgres/postgresql.conf`
```ini
password_encryption = scram-sha-256
log_connections = on
log_disconnections = on
```

### 2.3. Secretos
Ubicación: `infrastructure/secrets/`
- `db_password.txt`: Contraseña de superusuario (inyectada a la BD).
- `app_user_password.txt`: Contraseña de aplicación (usada por los servicios).

---

## 3. Evidencia de Seguridad y Pruebas

### 3.1. Verificación de Puertos (Desde el Host)
Para verificar que la base de datos no está expuesta, ejecute desde su terminal (PowerShell/Bash):

```bash
# Intentar conectar al puerto por defecto de Postgres (debe fallar)
Test-NetConnection -ComputerName localhost -Port 5432
# O usando netcat
nc -zv localhost 5432
```
**Resultado Esperado:** `Connection refused` o `TcpTestSucceeded : False`.

### 3.2. Verificación de Red Interna
Verifique que la red `backend-network` es interna:

```bash
docker network inspect admin2_backend-network
```
**Resultado Esperado:** `"Internal": true`

### 3.3. Prueba de Conexión desde Backend
Los servicios deben poder conectar usando el usuario `app_user`. Verifique los logs de un servicio (ej. `auth-service-1`) al iniciar:

```bash
docker logs auth-service-1
```
**Resultado Esperado:** Conexión exitosa a la base de datos y arranque del servidor (Uvicorn running).

### 3.4. Auditoría de Logs
Verifique que Postgres está registrando las conexiones:

```bash
docker logs auth-db
```
**Resultado Esperado:** Líneas como `LOG:  connection received: host=... user=app_user database=...`

---

## 4. Conclusión
La infraestructura de base de datos ha sido endurecida siguiendo las mejores prácticas de seguridad. La superficie de ataque se ha reducido drásticamente al eliminar la exposición de puertos, restringir privilegios de usuario y aislar la red.
