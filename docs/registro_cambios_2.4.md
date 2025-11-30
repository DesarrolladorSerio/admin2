# Registro de Cambios y Solución de Errores - Punto 2.4

Este documento detalla las correcciones y ajustes realizados para estabilizar el despliegue de los microservicios (Auth, Reservations, Notifications, Datos Municipalidad) y asegurar su correcta comunicación con la infraestructura (PostgreSQL, MinIO).

## 1. Auth Service (`auth-service`)

### Problema
El servicio fallaba al iniciar debido a dos razones:
1.  **Error de Importación**: `NameError: name 'os' is not defined`.
2.  **Condición de Carrera**: El servicio intentaba conectar a la base de datos antes de que esta estuviera lista, provocando un cierre inmediato (`CrashLoopBackOff`).

### Solución
*   **Archivo**: `services/auth-service/main.py`
*   **Cambios**:
    *   Se agregó `import os`.
    *   Se implementó una lógica de reintento (`retry logic`) en el evento `on_startup`. Ahora el servicio intenta conectar a la base de datos 30 veces con una espera de 2 segundos entre intentos, permitiendo que PostgreSQL termine su inicialización.

## 2. Reservations Service (`reservations-service`)

### Problema
El servicio iniciaba pero fallaba al crear las tablas con el error `InsufficientPrivilege`. El usuario `app_user` no tenía permisos para crear tablas en el esquema `public`.

### Solución
*   **Archivo**: `infrastructure/database/init/01-app-permissions.sh`
*   **Cambios**:
    *   Se actualizó el script de inicialización para otorgar explícitamente permisos de creación:
        ```bash
        GRANT USAGE, CREATE ON SCHEMA public TO app_user;
        ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO app_user;
        ```
    *   Se recrearon los volúmenes de base de datos para aplicar los nuevos permisos.

## 3. Notifications Service (`notifications-service`)

### Problema
El servicio fallaba con `IsADirectoryError: [Errno 21] Is a directory: '/run/secrets/smtp_password'`. Esto ocurría porque en el sistema de archivos local, `infrastructure/secrets/smtp_password.txt` se había creado accidentalmente como una carpeta en lugar de un archivo.

### Solución
*   **Infraestructura**:
    *   Se eliminó la carpeta `infrastructure/secrets/smtp_password.txt`.
    *   Se creó un archivo de texto válido con el mismo nombre conteniendo el secreto.

## 4. Datos Municipalidad Service (`datos-municipalidad-service`)

### Problema A: Conexión a MinIO
El servicio fallaba al conectar con MinIO con el error `S3 operation failed; code: InvalidAccessKeyId`.
*   **Causa**: El código en `storage_service.py` estaba usando `os.getenv` directamente, ignorando la lógica de carga de secretos desde archivos (Docker Secrets) definida en `config.py`.

### Solución A
*   **Archivo**: `services/datos-municipalidad-service/storage_service.py`
*   **Cambios**:
    *   Se modificó la clase `MinIOStorage` para importar y usar la instancia `settings` de `config.py`, asegurando que las credenciales se lean correctamente desde `/run/secrets/`.

### Problema B: Error de Librería Pydantic
Al reconstruir el servicio, falló con `PydanticImportError: BaseSettings has been moved to the pydantic-settings package`.
*   **Causa**: Incompatibilidad con versiones recientes de Pydantic v2.

### Solución B
*   **Archivo**: `services/datos-municipalidad-service/config.py`
*   **Cambios**:
    *   Se actualizó la importación: `from pydantic_settings import BaseSettings`.

## 5. Mantenimiento General de Docker

### Problemas de Caché
Se encontró un error de corrupción en el caché de construcción de Docker (`snapshot does not exist`).

### Solución
*   Se ejecutó `docker builder prune -f` para limpiar el caché corrupto.
*   Se forzó la recreación de contenedores y volúmenes específicos (`minio_data`) para asegurar un estado limpio de autenticación.

---

## Estado Final
Todos los servicios (`api-gateway`, `frontend`, `auth-service`, `reservations-service`, `documents-service`, `notifications-service`, `datos-municipalidad-service`) se encuentran en estado **Up (healthy)** y las conexiones a bases de datos y almacenamiento de objetos son exitosas.
