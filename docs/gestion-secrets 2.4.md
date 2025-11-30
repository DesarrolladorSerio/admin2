# Informe Técnico: Gestión de Secretos y Hardening (Punto 2.4)

**Estudiante:** Augusto Fuenzalida
**Fecha:** 30 de Noviembre de 2025
**Asignatura:** Administración de Redes / Seguridad en Sistemas
**Referencia:** Laboratorio - Proyecto Admin 3

---

## 1. Introducción
La gestión de secretos es un componente crítico en la seguridad de aplicaciones modernas. Este documento detalla la estrategia implementada para manejar credenciales, claves API y certificados, asegurando que ninguna información sensible sea expuesta en el código fuente, logs o inspecciones de contenedores.

## 2. Docker Secrets: Profundización Técnica

La gestión de secretos mediante **Docker Secrets** se ha establecido como el mecanismo principal para la inyección segura de credenciales en el proyecto.

### 2.1. Arquitectura de Funcionamiento
A diferencia de las variables de entorno tradicionales, Docker Secrets utiliza un sistema de montaje en memoria que evita la persistencia en disco dentro del contenedor.

```ascii
+---------------------+       +-----------------------+       +-----------------------------+
|  Host (Servidor)    |       |    Docker Engine      |       |   Contenedor (Runtime)      |
|                     |       |                       |       |                             |
|  ./secrets/db_pass  | ----> |  Montaje Seguro (RO)  | ----> |  /run/secrets/db_password   |
|  (Archivo Protegido)|       |      (tmpfs)          |       |  (Memoria RAM - Read Only)  |
+---------------------+       +-----------------------+       +-----------------------------+
```

1.  **Inyección**: El archivo del host se monta directamente en `/run/secrets/` dentro del contenedor.
2.  **Volatilidad**: Al residir en `tmpfs` (sistema de archivos temporal en RAM), los secretos no se escriben en la capa de escritura del contenedor (COW), evitando que queden rastros si se exporta la imagen o se inspecciona el disco.
3.  **Seguridad**: No son visibles mediante `docker inspect`, a diferencia de las variables de entorno (`ENV`), que exponen sus valores en texto plano en la metadata del contenedor.

### 2.2. Implementación en el Proyecto
En el archivo `docker-compose.yml`, los secretos se definen explícitamente:

```yaml
secrets:
  db_password:
    file: ./infrastructure/secrets/db_password.txt

services:
  auth-service:
    secrets:
      - db_password
    environment:
      DATABASE_URL_FILE: /run/secrets/db_password
```
Las aplicaciones (Python/Node.js) han sido modificadas para leer desde `_FILE`, priorizando la lectura del archivo secreto sobre la variable de entorno directa.

---

## 3. Gestión de Archivos de Entorno (.env)

### 3.1. Diferencia Crítica: `.env` vs `.env.example`

| Característica | `.env` | `.env.example` |
| :--- | :--- | :--- |
| **Contenido** | Valores REALES y SENSIBLES (contraseñas, keys). | Valores FICTICIOS o vacíos (placeholders). |
| **Propósito** | Configuración del entorno de ejecución local/prod. | Documentación de variables requeridas. |
| **Control de Versiones** | **NUNCA** se sube a Git (`.gitignore`). | **SIEMPRE** se sube a Git. |
| **Seguridad** | Alta (debe protegerse). | Pública (información no sensible). |

### 3.2. Flujo de Trabajo Seguro
1.  El desarrollador clona el repositorio.
2.  Copia `.env.example` a `.env`: `cp .env.example .env`.
3.  Rellena `.env` con las credenciales locales o de desarrollo.
4.  El archivo `.env` permanece local y nunca abandona la máquina del desarrollador.

---

## 4. Estrategia de Rotación de Secretos

La rotación es la práctica de cambiar credenciales periódicamente para minimizar el impacto de una posible filtración.

### 4.1. Ciclo de Vida de un Secreto (Conceptual)

```ascii
   [ Fase 1: Normal ]        [ Fase 2: Transición ]        [ Fase 3: Limpieza ]
   
   +--------------+          +--------------+              +--------------+
   |  Secreto A   |          |  Secreto A   | (Válido)     |              |
   |   (Activo)   |          |      +       |              |  Secreto B   |
   |              |          |  Secreto B   | (Nuevo)      |   (Activo)   |
   +--------------+          +--------------+              +--------------+
                                     ^
                                     |
                            Actualizar App para
                            aceptar ambos o
                            cambiar referencia
```

### 4.2. Procedimiento de Rotación en Docker Compose
1.  **Generar**: Crear un nuevo archivo de secreto, ej. `db_password_v2.txt`.
2.  **Configurar**: Actualizar `docker-compose.yml` para apuntar al nuevo archivo.
    ```yaml
    secrets:
      db_password:
        file: ./infrastructure/secrets/db_password_v2.txt
    ```
3.  **Desplegar**: Ejecutar `docker-compose up -d`. Docker recreará los contenedores montando el nuevo secreto.
4.  **Verificar**: Confirmar que los servicios funcionan correctamente.
5.  **Archivar**: Eliminar el archivo `db_password.txt` antiguo de forma segura.

---

## 5. Buenas Prácticas y Hardening

### 5.1. Permisos de Archivo (File Permissions)
Los archivos de secretos en el host (`infrastructure/secrets/*.txt`) deben tener permisos restrictivos para evitar lecturas no autorizadas por otros usuarios del sistema operativo.

*   **Recomendado**: `chmod 600` (Lectura/Escritura solo para el dueño).
*   **Propietario**: El usuario que ejecuta el daemon de Docker o el proceso de despliegue.

### 5.2. Auditoría y Logs
*   **Regla de Oro**: Nunca imprimir el contenido de variables de entorno o secretos en los logs de la aplicación.
*   **Sanitización**: Configurar los loggers de la aplicación para ofuscar patrones que parezcan tarjetas de crédito, tokens o contraseñas.

### 5.3. Inventario
Mantener un inventario (documento separado y seguro) de:
*   Qué secretos existen.
*   Dónde se utilizan.
*   Fecha de última rotación.
*   Responsable de la custodia.

---

## 6. Verificación de Repositorio Limpio

Para garantizar que no se han filtrado secretos en el historial de Git, se aplicaron las siguientes medidas correctivas y preventivas:

### 6.1. Configuración de `.gitignore`
El archivo `.gitignore` incluye explícitamente las rutas de secretos para prevenir su inclusión accidental:

```gitignore
# Secretos e Infraestructura
infrastructure/secrets/*
!infrastructure/secrets/.gitkeep
.env
*.pem
*.key
```

### 6.2. Limpieza del Índice (Git Index)
Durante el desarrollo, se detectó que algunos archivos de secretos habían sido rastreados. Se procedió a eliminarlos del índice sin borrarlos del disco local:

```bash
git rm --cached infrastructure/secrets/app_user_password.txt
git rm --cached infrastructure/secrets/db_password.txt
```
Esto asegura que los archivos existan en el servidor para el despliegue, pero no en el repositorio remoto.

### 6.3. Escaneo de Fugas
Se recomienda el uso de herramientas como **TruffleHog** o **GitLeaks** en el pipeline de CI/CD para bloquear commits que contengan cadenas de alta entropía o patrones de claves conocidas.

---

## 7. Conclusión

La implementación de **Docker Secrets**, combinada con una estricta política de manejo de archivos `.env` y la limpieza del repositorio, ha elevado significativamente el nivel de seguridad del proyecto. La arquitectura actual garantiza que las credenciales vivan únicamente en la memoria de los procesos que las necesitan, cumpliendo con los principios de **Defensa en Profundidad** y **Privilegio Mínimo**. El sistema está preparado para operar en entornos productivos con riesgos de exposición de datos minimizados.
