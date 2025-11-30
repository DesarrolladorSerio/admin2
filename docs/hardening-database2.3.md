# Informe Técnico: Hardening de Bases de Datos

**Estudiante:** Augusto Fuenzalida
**Fecha:** 30 de Noviembre de 2025
**Asignatura:** Administración de Redes / Seguridad en Sistemas
**Referencia:** Laboratorio - Proyecto Admin 3 (Punto 2.3)

---

## 1. Objetivo de la Actividad
El objetivo de esta sección fue asegurar la infraestructura de datos del proyecto mediante la implementación de controles de acceso estrictos, cifrado de credenciales y aislamiento de red. Se aplicaron configuraciones avanzadas en PostgreSQL para cumplir con el principio de privilegio mínimo y defensa en profundidad.

## 2. Medidas de Seguridad Implementadas

### 2.1. Autenticación Obligatoria y Cifrado (SCRAM-SHA-256)
Se ha configurado PostgreSQL para rechazar cualquier método de autenticación débil (como `md5` o `trust` en red) y exigir el uso de **SCRAM-SHA-256** (Salted Challenge Response Authentication Mechanism).

**Explicación Técnica:**
A diferencia de MD5, SCRAM-SHA-256 previene ataques de *Pass-the-Hash* y *Rainbow Tables*. El servidor nunca almacena la contraseña en texto plano ni su hash directo; en su lugar, almacena parámetros de sal y iteración que obligan al cliente a probar su identidad sin enviar la contraseña por la red.

**Configuración en `postgresql.conf`:**
```ini
# Security
password_encryption = scram-sha-256
```

### 2.2. Usuario de Aplicación con Privilegios Mínimos
Se eliminó la práctica insegura de conectar los microservicios utilizando el superusuario `postgres`. Se creó un rol dedicado `app_user` con permisos granulares.

**Script de Inicialización (`infrastructure/database/init/01-app-permissions.sh`):**
Este script se ejecuta al inicio del contenedor para garantizar que los permisos sean correctos y seguros.

```bash
#!/bin/bash
# ... (Lectura segura del secreto app_user_password) ...

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Creación idempotente del usuario
    DO \$do\$
    BEGIN
       IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'app_user') THEN
          CREATE USER app_user WITH PASSWORD '$APP_USER_PASSWORD';
       END IF;
    END \$do\$;

    -- 1. Revocar permisos públicos por defecto (Hardening crítico)
    REVOKE ALL ON SCHEMA public FROM public;
    
    -- 2. Otorgar solo uso y creación de objetos en esquema public
    GRANT USAGE, CREATE ON SCHEMA public TO app_user;
    
    -- 3. Asegurar que tablas futuras pertenezcan o sean accesibles por app_user
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO app_user;
EOSQL
```

### 2.3. Control de Acceso a Red (pg_hba.conf)
El archivo `pg_hba.conf` (Host-Based Authentication) actúa como un firewall a nivel de aplicación. Se configuró una política de "Deny All" por defecto, permitiendo solo conexiones desde las subredes privadas de Docker.

**Archivo Completo (`infrastructure/database/postgres/pg_hba.conf`):**
```properties
# PostgreSQL Client Authentication Configuration File

# TYPE  DATABASE        USER            ADDRESS                 METHOD

# "local" is for Unix domain socket connections only
local   all             all                                     trust

# IPv4 local connections:
# Permitir rangos de red interna de Docker (172.16.x.x, 10.x.x.x, etc.)
host    all             all             172.16.0.0/12           scram-sha-256
host    all             all             192.168.0.0/16          scram-sha-256
host    all             all             10.0.0.0/8              scram-sha-256

# REGLA FINAL: Rechazar explícitamente todo lo demás (Internet/Host)
host    all             all             0.0.0.0/0               reject
```

### 2.4. Auditoría y Logging
Se habilitó el registro de eventos de conexión para auditoría forense en `postgresql.conf`.

```ini
# Logging and Auditing
log_connections = on        # Registra intentos de login exitosos
log_disconnections = on     # Registra fin de sesiones
log_line_prefix = '%m [%p] %u@%d ' # Formato: Timestamp [PID] User@DB
log_statement = 'none'      # Evita loguear queries con datos sensibles
```

## 3. Arquitectura de Aislamiento de Red

Las bases de datos residen en una red aislada (`backend-network`) sin acceso directo desde el exterior.

```ascii
      INTERNET
         |
   +-----+------+
   |  Frontend  | (Public Network)
   +-----+------+
         |
   +-----+------+
   | API Gateway| (Public & App Network)
   +-----+------+
         |
   +-----+------+      +------------------+
   | Micro-     |      |   Red Aislada    |
   | servicios  | <--> | (backend-network)|
   +------------+      |   [ Postgres ]   |
                       |   [  Redis   ]   |
                       |   (Sin Puertos   |
                       |    Expuestos)    |
                       +------------------+
```

## 4. Evidencia de Seguridad y Pruebas

### 4.1. Verificación de NO Exposición de Puertos
Se verificó que los contenedores de base de datos no publican puertos en el host (0.0.0.0).

**Prueba con `docker inspect`:**
```powershell
docker inspect -f '{{.NetworkSettings.Ports}}' auth-db
# Resultado: map[5432/tcp:[]]
# (Los corchetes vacíos indican que NO hay mapeo al host)
```

**Prueba de Conectividad (Netcat/Test-NetConnection):**
Desde la máquina host, el intento de conexión directa falla, confirmando el aislamiento.
```powershell
Test-NetConnection -ComputerName localhost -Port 5432
# WARNING: TCP connect to (::1 : 5432) failed
# TcpTestSucceeded : False
```

### 4.2. Verificación de Autenticación SCRAM
Al inspeccionar la tabla `pg_shadow` dentro del contenedor, se confirma el algoritmo de hash.

```sql
SELECT usename, passwd FROM pg_shadow WHERE usename = 'app_user';
-- Resultado:
-- usename  | passwd
-- app_user | SCRAM-SHA-256$4096:xS... (Hash seguro)
```

## 5. Conclusión
La capa de persistencia del proyecto ha sido asegurada siguiendo estándares robustos. La combinación de **autenticación SCRAM-SHA-256**, **roles con privilegios mínimos**, **listas de control de acceso (pg_hba)** y **aislamiento de red** garantiza que los datos estén protegidos contra accesos no autorizados, movimientos laterales y ataques de fuerza bruta desde la red externa. La base de datos es accesible única y exclusivamente por los microservicios autorizados dentro de la red privada de Docker.

