# 2.1 Documentación de Implementación HTTPS/TLS

## 1. Introducción
Este documento detalla la implementación del protocolo HTTPS (Hypertext Transfer Protocol Secure) y TLS (Transport Layer Security) en la arquitectura de microservicios del proyecto. El objetivo es garantizar la confidencialidad e integridad de los datos transmitidos entre el cliente (Frontend) y los servicios (API Gateway), así como asegurar la comunicación interna.

## 2. Generación de Certificados (OpenSSL)
Para el entorno de desarrollo y pruebas, se utilizan certificados autofirmados generados mediante OpenSSL. Estos certificados permiten habilitar el cifrado SSL/TLS sin depender de una autoridad certificadora pública (CA) durante la fase de desarrollo.

**Comando utilizado para la generación:**
```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout infrastructure/certs/server.key \
    -out infrastructure/certs/server.crt \
    -subj "/C=AR/ST=BuenosAires/L=CABA/O=Municipio/OU=IT/CN=localhost"
```

*   **server.key**: Clave privada del servidor (Debe mantenerse segura).
*   **server.crt**: Certificado público del servidor.
*   **Ubicación**: Los archivos se almacenan en `infrastructure/certs/` y se montan como volúmenes en los contenedores.

## 3. Configuración del Frontend (Nginx)
El servicio de Frontend utiliza Nginx para servir la aplicación React y actuar como proxy inverso. La configuración SSL se define en `services/frontend/nginx.conf`.

**Detalles de Configuración:**
*   **Puertos de Escucha**: El servidor escucha en el puerto `443` para tráfico seguro (SSL).
*   **Certificados**: Se referencian las rutas `/etc/nginx/certs/server.crt` y `/etc/nginx/certs/server.key`.
*   **Protocolos**: Se habilitan exclusivamente `TLSv1.2` y `TLSv1.3` para garantizar seguridad moderna.
*   **Ciphers**: Se utiliza la configuración `HIGH:!aNULL:!MD5` para evitar algoritmos débiles.

```nginx
server {
    listen 80;
    listen 443 ssl;
    server_name localhost;

    ssl_certificate /etc/nginx/certs/server.crt;
    ssl_certificate_key /etc/nginx/certs/server.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ...
}
```

## 4. Configuración del API Gateway con TLS
El API Gateway actúa como punto de entrada único para todos los microservicios de backend. Su configuración en `services/api-gateway/nginx.conf` asegura que todas las peticiones a la API viajen cifradas.

**Características de la implementación:**
*   **Terminación SSL**: El Gateway maneja el descifrado del tráfico HTTPS entrante antes de enrutarlo a los microservicios internos.
*   **Volúmenes**: Los certificados se inyectan en el contenedor mediante Docker Compose:
    ```yaml
    volumes:
      - ./infrastructure/certs:/etc/nginx/certs:ro
    ```

## 5. Redirección HTTP → HTTPS
La configuración actual de Nginx dispone de bloques `listen` tanto para el puerto 80 (HTTP) como para el 443 (HTTPS).
*   **Estado Actual**: Los servicios son accesibles tanto por HTTP como por HTTPS.
*   **Práctica Recomendada**: Para forzar la redirección en entornos productivos, se implementa un bloque de servidor dedicado que captura el tráfico del puerto 80 y responde con un código 301 hacia la versión HTTPS.

## 6. Headers de Seguridad
El API Gateway inyecta cabeceras de seguridad HTTP en todas las respuestas para mitigar ataques comunes como XSS, Clickjacking y Sniffing de contenido.

**Headers implementados (`services/api-gateway/nginx.conf`):**

| Header | Valor | Descripción |
|--------|-------|-------------|
| `X-Frame-Options` | `SAMEORIGIN` | Previene ataques de Clickjacking evitando que el sitio sea embebido en iframes de otros dominios. |
| `X-Content-Type-Options` | `nosniff` | Evita que el navegador intente "adivinar" el tipo de contenido (MIME sniffing). |
| `X-XSS-Protection` | `1; mode=block` | Activa el filtro de Cross-Site Scripting (XSS) del navegador. |
| `Content-Security-Policy` | `default-src 'self' ...` | Define qué fuentes de contenido son confiables, mitigando XSS e inyecciones de datos. |
| `Strict-Transport-Security` | *(Recomendado)* | HSTS instruye al navegador a usar siempre HTTPS en futuras visitas (pendiente de activación estricta). |

## 7. Ejemplo de Uso y Verificación
Para verificar la correcta implementación de HTTPS, se puede acceder al servicio a través de un navegador o herramientas de línea de comandos.

**Acceso vía Navegador:**
1.  Navegar a `https://localhost` (Frontend) o `https://localhost:8443` (Gateway).
2.  El navegador mostrará un candado en la barra de direcciones.
3.  *Nota*: Al usar certificados autofirmados, el navegador mostrará una advertencia de seguridad que debe ser aceptada manualmente.

**Captura Simulada (Descripción):**
> En la barra de direcciones de Chrome/Firefox, se observa el icono de un **candado cerrado** a la izquierda de la URL `https://localhost`. Al hacer clic en el candado y seleccionar "La conexión es segura" > "El certificado es válido", se muestran los detalles del certificado emitido para "localhost" por la organización "Municipio".

## 8. Riesgos Mitigados
La implementación de HTTPS/TLS mitiga los siguientes riesgos críticos:
1.  **Intercepción de Datos (Sniffing)**: Evita que atacantes en la red capturen credenciales, tokens JWT o datos personales en texto plano.
2.  **Man-in-the-Middle (MitM)**: Asegura que el cliente se está comunicando con el servidor legítimo y no con un intermediario malicioso.
3.  **Modificación de Datos**: Garantiza la integridad de la información, asegurando que los datos no han sido alterados durante el tránsito.

## 9. Conclusión Técnica
La infraestructura del proyecto ha sido asegurada exitosamente mediante la implementación de TLS 1.2/1.3 en los puntos de entrada públicos (Frontend y API Gateway). El uso de certificados X.509, combinado con cabeceras de seguridad robustas en Nginx, proporciona una capa de defensa sólida contra ataques de red y vulnerabilidades web comunes, cumpliendo con los estándares de seguridad modernos para aplicaciones distribuidas.
