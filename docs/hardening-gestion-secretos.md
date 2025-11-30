# Informe Técnico: Gestión de Secretos y Hardening (Punto 2.4)

**Referencia:** Proyecto Admin 3 - Seguridad y Hardening
**Tema:** Gestión Segura de Credenciales y Secretos

---

## 1. Docker Secrets: Profundización Técnica

La gestión de secretos mediante **Docker Secrets** es el estándar de seguridad para manejar información sensible (contraseñas, claves API, certificados) en entornos contenerizados, superando las limitaciones de las variables de entorno tradicionales.

### 1.1. Funcionamiento Interno
A diferencia de las variables de entorno que se inyectan al iniciar el contenedor y permanecen visibles en la inspección del mismo (`docker inspect`), los Docker Secrets funcionan mediante un sistema de montaje de archivos en memoria:

1.  **Almacenamiento Seguro**: En entornos Docker Swarm, los secretos se almacenan encriptados (Raft logs) en el disco del nodo manager. En Docker Compose (nuestro caso), se gestionan como archivos locales pero se montan de la misma manera segura en el contenedor.
2.  **Montaje en `tmpfs`**: Los secretos no se escriben en el disco del contenedor. Se montan en un sistema de archivos temporal en memoria (`tmpfs`), típicamente en la ruta `/run/secrets/<nombre_secreto>`.
3.  **Volatilidad**: Si el contenedor se detiene, el secreto desaparece de la memoria RAM, reduciendo la superficie de ataque ante análisis forenses de disco.

### 1.2. Ventajas sobre Variables de Entorno
*   **No visibles en `docker inspect`**: Las variables de entorno pueden ser leídas por cualquier usuario con acceso al daemon de Docker. Los secretos no aparecen en la metadata del contenedor.
*   **No se filtran en logs**: Es común que aplicaciones vuelquen sus variables de entorno en logs de error. Al usar archivos, se evita este riesgo accidental.
*   **Control de Acceso Granular**: Solo los servicios que explícitamente solicitan el secreto en su definición (`docker-compose.yml`) tienen acceso a él.

### 1.3. Consumo desde Aplicaciones
Las aplicaciones deben ser programadas para leer el contenido de un archivo en lugar de una variable de entorno directa.
*   **Python**: Se utiliza `open('/run/secrets/mi_secreto').read().strip()`.
*   **Node.js**: Se utiliza `fs.readFileSync('/run/secrets/mi_secreto', 'utf8')`.
*   **Go**: Se utiliza `ioutil.ReadFile("/run/secrets/mi_secreto")`.

---

## 2. Gestión de Archivos de Entorno (.env)

### 2.1. Diferencia entre `.env` y `.env.example`
*   **`.env`**: Es el archivo que contiene la configuración real y sensible del entorno local o de producción. **Nunca** debe ser versionado en el control de fuentes (Git).
*   **`.env.example`**: Es una plantilla que documenta qué variables requiere la aplicación para funcionar. Contiene valores ficticios o vacíos y **sí** debe ser versionado.

### 2.2. Buenas Prácticas
*   **Nomenclatura**: Usar mayúsculas y guiones bajos (ej. `DB_PASSWORD`, `API_KEY`).
*   **Gitignore**: Asegurar que `.env` esté explícitamente en el archivo `.gitignore` global y del proyecto.
*   **Uso como Plantilla**: Un nuevo desarrollador debe poder clonar el repositorio, copiar `.env.example` a `.env`, y tener un entorno funcional (o saber qué valores rellenar) sin adivinar configuraciones.

---

## 3. Proceso de Rotación de Secretos

La rotación de secretos es la práctica de cambiar periódicamente las credenciales para limitar el impacto si una de ellas es comprometida.

### 3.1. ¿Por qué es necesario?
*   **Mitigación de Fugas**: Si una clave antigua se filtra, ya no será válida.
*   **Cumplimiento Normativo**: Muchos estándares (PCI-DSS, ISO 27001) exigen rotación periódica.

### 3.2. Flujo de Rotación (Conceptual)
1.  **Generación**: Se crea un nuevo secreto (ej. `db_password_v2`).
2.  **Actualización de Infraestructura**: Se actualiza la base de datos o servicio externo para aceptar la nueva contraseña, manteniendo temporalmente la anterior si es posible (rotación sin caída).
3.  **Actualización del Servicio**: Se modifica la definición del servicio (Docker Compose/Swarm) para apuntar al nuevo secreto.
4.  **Redespliegue**: Se reinician los contenedores. Al levantar, leerán el nuevo valor desde `/run/secrets/`.
5.  **Revocación**: Se elimina o invalida la credencial antigua en el sistema de origen.

### 3.3. Frecuencia Recomendada
*   **Críticos (BD, Claves Maestras)**: Cada 30-90 días.
*   **Tokens de Servicio**: Rotación automática diaria o semanal si la arquitectura lo permite.
*   **Inmediata**: Ante cualquier sospecha de incidente de seguridad.

---

## 4. Buenas Prácticas de Gestión de Secretos

Para mantener un entorno endurecido ("hardened"), se deben seguir estas directrices:

1.  **Almacenamiento Externo**: Los secretos nunca deben estar "hardcoded" en el código fuente ni en la imagen Docker. Siempre deben inyectarse en tiempo de ejecución.
2.  **Principio de Menor Privilegio**: Un contenedor solo debe montar los secretos estrictamente necesarios para su función.
3.  **Permisos de Archivo (File Permissions)**:
    *   Los archivos de secretos en el host deben tener permisos restrictivos (ej. `600` o `400`), propiedad solo del usuario root o del usuario encargado del despliegue.
4.  **Inventario de Secretos**: Mantener un registro (fuera del código) de qué secretos existen, quién los usa y cuándo expiran.
5.  **Monitoreo de Acceso**: En entornos avanzados, auditar quién y cuándo accede a los sistemas de gestión de claves (Vault, AWS Secrets Manager, etc.).
6.  **Limpieza de Logs**: Configurar las aplicaciones para que nunca impriman el contenido de los secretos en los logs de salida estándar o archivos de registro.

---

## 5. Verificación y Auditoría

Es crucial verificar periódicamente que no existan fugas de información en el repositorio.

### 5.1. Búsqueda de Secretos en el Código
Antes de realizar un `commit` o durante auditorías, se pueden utilizar herramientas o comandos simples para buscar patrones sospechosos.

**Comandos de ejemplo:**

*Buscar la palabra "password" en todo el directorio, mostrando número de línea:*
```bash
grep -R "password" -n .
```

*Buscar la palabra "secret" o claves potenciales:*
```bash
grep -R "secret" -n .
grep -R "API_KEY" -n .
```

### 5.2. Revisión Pre-Commit
*   Verificar que no se estén subiendo archivos `.env`, `.pem`, `.key` o carpetas de configuración privada.
*   Revisar los `diff` para asegurar que no se agregaron credenciales "para probar rápido" y se olvidó borrarlas.
