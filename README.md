# admin 3

## Gestión y Rotación de Secretos

Este proyecto utiliza **Docker Secrets** para gestionar credenciales sensibles de forma segura, cumpliendo con los estándares de seguridad requeridos.

### Cómo se generan los secretos
Los secretos se generan automáticamente mediante scripts de seguridad o manualmente, y se almacenan en la carpeta `infrastructure/secrets/`.

### Dónde se guardan
- **Ubicación:** `infrastructure/secrets/`
- **Formato:** Archivos de texto plano que contienen únicamente el valor del secreto (sin saltos de línea extra ni comentarios).

### Archivos que NO se deben subir a git
El archivo `.gitignore` está configurado para excluir estrictamente:
- `.env` (Variables de entorno locales)
- `infrastructure/secrets/*` (Credenciales reales)
- Solo se permite `infrastructure/secrets/.gitkeep` para mantener la estructura de carpetas.

### Cómo usar .env.example
El archivo `.env.example` contiene una plantilla de las variables de entorno necesarias para el despliegue.
1. Copie el archivo: `cp .env.example .env`
2. Edite `.env` con sus valores de configuración (puertos, hosts, etc.).
3. **Importante:** Las credenciales críticas (contraseñas de DB, JWT secrets, claves de API) deben gestionarse vía Docker Secrets. El archivo `.env` solo debe contener configuración no sensible o referencias a archivos de secretos.

### Cómo funciona la rotación
Se proporciona un script automatizado para rotar los secretos y reiniciar los servicios.

**Uso:**
```bash
./scripts/security/rotate-secrets.sh
```

Este script realiza las siguientes acciones:
1. Genera nuevos valores aleatorios criptográficamente seguros (hex 32 chars) usando `openssl`.
2. Sobrescribe los archivos en `infrastructure/secrets/` (DB password, JWT secret, MinIO keys).
3. Reinicia los contenedores Docker para que los servicios tomen los nuevos secretos.

### Cómo regenerar secretos en caso de incidente
Si sospecha que un secreto ha sido comprometido:
1. Ejecute el script de rotación inmediatamente: `./scripts/security/rotate-secrets.sh`.
2. Verifique los logs de los servicios para asegurar que reiniciaron correctamente y conectan con las nuevas credenciales.
3. Si utiliza servicios externos (ej. SMTP), cambie la contraseña en el proveedor y actualice el archivo `infrastructure/secrets/smtp_password.txt` manualmente antes de reiniciar.
