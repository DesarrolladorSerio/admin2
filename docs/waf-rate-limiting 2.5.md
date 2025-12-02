# 2.5 Documentación de Implementación WAF y Rate Limiting

## 1. Introducción
Este documento detalla la implementación de medidas de seguridad a nivel de aplicación (WAF - Web Application Firewall) y control de tráfico (Rate Limiting) en el API Gateway. El objetivo es proteger la infraestructura contra ataques de denegación de servicio (DoS), fuerza bruta y escaneos de vulnerabilidades automatizados.

## 2. Configuración de Rate Limiting (Nginx)
El API Gateway utiliza el módulo `ngx_http_limit_req_module` de Nginx para limitar la tasa de procesamiento de peticiones. Se han definido dos zonas de limitación principales en `services/api-gateway/nginx.conf`.

### 2.1 Zonas de Limitación
1.  **Límite Global (`global_limit`)**:
    *   **Objetivo**: Proteger el sistema general contra sobrecarga.
    *   **Tasa**: 10 peticiones por segundo (10r/s).
    *   **Burst**: 20 peticiones (permite picos breves de tráfico).
    *   **Clave**: `$binary_remote_addr` (IP del cliente).

2.  **Límite de Login (`login_limit`)**:
    *   **Objetivo**: Prevenir ataques de fuerza bruta contra el endpoint de autenticación.
    *   **Tasa**: 1 petición por segundo (1r/s).
    *   **Burst**: 5 peticiones.
    *   **Clave**: `$binary_remote_addr`.

**Configuración en `nginx.conf`:**
```nginx
http {
    # Definición de zonas
    limit_req_zone $binary_remote_addr zone=global_limit:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login_limit:10m rate=1r/s;

    server {
        # Aplicación del límite global
        limit_req zone=global_limit burst=20 nodelay;

        # Aplicación específica para Login
        location /api/auth/token {
            limit_req zone=login_limit burst=5 nodelay;
            proxy_pass http://auth_service;
        }
    }
}
```

## 3. Bloqueo de Agentes Maliciosos (WAF Básico)
Se ha implementado un filtrado basado en el encabezado `User-Agent` para bloquear herramientas de escaneo de vulnerabilidades conocidas.

**Regla de Bloqueo:**
Si el `User-Agent` coincide con herramientas como `sqlmap`, `nikto`, `nmap`, etc., el servidor responde inmediatamente con un error `403 Forbidden`.

```nginx
if ($http_user_agent ~* (sqlmap|nikto|w3af|nmap|nessus)) {
    return 403;
}
```

## 4. Verificación y Pruebas
Para validar la efectividad de estas medidas, se ha desarrollado un script de pruebas automatizado ubicado en `tests/security/rate-limit-test.sh`.

### 4.1 Metodología de Prueba
El script realiza las siguientes validaciones:
1.  **Prueba de WAF**: Envía una petición simulando ser `sqlmap`. Se espera un código `403`.
2.  **Prueba de Carga Global**: Lanza 200 peticiones concurrentes al endpoint raíz `/`. Se espera que el servidor responda con `429 Too Many Requests` una vez superado el umbral.
3.  **Prueba de Fuerza Bruta (Login)**: Lanza peticiones concurrentes al endpoint de login. Se espera `429`.

### 4.2 Ejecución
```bash
bash tests/security/rate-limit-test.sh
```

**Resultados Esperados:**
*   Bloqueo de User-Agent: **ÉXITO (HTTP 403)**.
*   Rate Limit Global: **ÉXITO** (Detección de múltiples respuestas HTTP 429).
*   Rate Limit Login: **ÉXITO** (Detección de respuestas HTTP 429 en `/api/auth/token`).
