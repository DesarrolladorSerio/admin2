# 📧 Servicio de Notificaciones

Servicio de notificaciones con envío de emails y sistema de colas asíncrono usando Celery + Redis.

## 🚀 Características

- ✉️ **Envío de Emails**: Soporte para HTML, texto plano y adjuntos
- 🔄 **Sistema de Cola**: Procesamiento asíncrono con Celery + Redis
- 📝 **Templates HTML**: Templates profesionales para diferentes tipos de notificaciones
- 🔁 **Reintentos Automáticos**: Sistema de reintentos en caso de fallo
- 📊 **Monitoreo**: Endpoints para verificar estado de tareas
- 🎯 **Múltiples Tipos**: Confirmaciones, recordatorios, cancelaciones, documentos, etc.

## 📦 Dependencias

- **FastAPI**: Framework web
- **Celery**: Sistema de cola de tareas
- **Redis**: Broker para Celery
- **aiosmtplib**: Cliente SMTP asíncrono
- **Jinja2**: Motor de templates
- **email-validator**: Validación de emails

## 🔧 Configuración

### Variables de Entorno (.env)

```env
# Configuración SMTP
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu-email@gmail.com
SMTP_PASSWORD=tu-contraseña-de-aplicacion
SMTP_FROM_EMAIL=noreply@sistema.com
SMTP_FROM_NAME=Sistema de Reservas
SMTP_TLS=true

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Puerto del servicio
NOTIFICATIONS_SERVICE_PORT=8004
```

### Configuración de Gmail

Para usar Gmail como servidor SMTP:

1. Habilita la verificación en 2 pasos en tu cuenta de Google
2. Genera una "Contraseña de aplicación":
   - Ve a https://myaccount.google.com/apppasswords
   - Genera una nueva contraseña de aplicación
   - Usa esta contraseña en `SMTP_PASSWORD`

## 🏗️ Arquitectura

```
┌─────────────────┐
│   API Gateway   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────┐
│  Notifications  │────▶│    Redis    │
│    Service      │     │   (Queue)   │
│   (FastAPI)     │     └─────────────┘
└─────────────────┘            │
                               ▼
                        ┌─────────────┐
                        │   Celery    │
                        │   Worker    │
                        └──────┬──────┘
                               │
                               ▼
                        ┌─────────────┐
                        │ SMTP Server │
                        │  (Gmail)    │
                        └─────────────┘
```

## 📋 API Endpoints

### Health Check
```bash
GET /health
```

### Envío de Email Genérico
```bash
POST /api/notifications/email
{
  "to_emails": ["usuario@example.com"],
  "subject": "Asunto del email",
  "html_body": "<h1>Hola</h1>",
  "text_body": "Hola",  # opcional
  "cc": [],  # opcional
  "bcc": []  # opcional
}
```

### Confirmación de Reserva
```bash
POST /api/notifications/reservation/confirmation
{
  "user_email": "usuario@example.com",
  "user_name": "Juan Pérez",
  "reservation_data": {
    "id": 123,
    "date": "2025-11-10",
    "time": "10:00",
    "service": "Licencia de Conducir",
    "location": "Oficina Centro"
  }
}
```

### Recordatorio de Reserva
```bash
POST /api/notifications/reservation/reminder
{
  "user_email": "usuario@example.com",
  "user_name": "Juan Pérez",
  "reservation_data": { ... }
}
```

### Cancelación de Reserva
```bash
POST /api/notifications/reservation/cancellation
{
  "user_email": "usuario@example.com",
  "user_name": "Juan Pérez",
  "reservation_data": { ... }
}
```

### Notificación de Documento
```bash
POST /api/notifications/document
{
  "user_email": "usuario@example.com",
  "user_name": "Juan Pérez",
  "document_data": {
    "name": "Documento.pdf",
    "type": "Identificación",
    "upload_date": "2025-11-06"
  },
  "notification_type": "uploaded"  # uploaded, approved, rejected
}
```

### Email de Bienvenida
```bash
POST /api/notifications/welcome
{
  "user_email": "usuario@example.com",
  "user_name": "Juan Pérez",
  "temp_password": "temporal123"  # opcional
}
```

### Recuperación de Contraseña
```bash
POST /api/notifications/password-reset
{
  "user_email": "usuario@example.com",
  "user_name": "Juan Pérez",
  "reset_token": "abc123xyz",
  "reset_url": "https://sistema.com/reset-password"
}
```

### Envío en Lote
```bash
POST /api/notifications/batch
{
  "emails": [
    {
      "to_emails": ["user1@example.com"],
      "subject": "Asunto 1",
      "html_body": "<p>Contenido 1</p>"
    },
    {
      "to_emails": ["user2@example.com"],
      "subject": "Asunto 2",
      "html_body": "<p>Contenido 2</p>"
    }
  ]
}
```

### Consultar Estado de Tarea
```bash
GET /api/notifications/task/{task_id}
```

Respuesta:
```json
{
  "task_id": "abc-123-xyz",
  "status": "SUCCESS",  # PENDING, STARTED, SUCCESS, FAILURE, RETRY
  "result": {
    "status": "success",
    "recipient": "usuario@example.com"
  }
}
```

### Estadísticas
```bash
GET /api/notifications/stats
```

## 🎨 Templates Disponibles

1. **reservation_confirmation.html** - Confirmación de reserva
2. **reservation_reminder.html** - Recordatorio de reserva
3. **reservation_cancellation.html** - Cancelación de reserva
4. **document_notification.html** - Notificación de documento
5. **welcome.html** - Email de bienvenida
6. **password_reset.html** - Recuperación de contraseña

## 🔄 Sistema de Cola

### Iniciar Celery Worker

```bash
# Desde el directorio del servicio
celery -A celery_config worker --loglevel=info

# Con concurrencia específica
celery -A celery_config worker --loglevel=info --concurrency=4

# En producción con autoscale
celery -A celery_config worker --loglevel=info --autoscale=10,3
```

### Monitorear Celery

```bash
# Ver tareas activas
celery -A celery_config inspect active

# Ver tareas programadas
celery -A celery_config inspect scheduled

# Ver estadísticas
celery -A celery_config inspect stats
```

## 🐳 Docker

### Construir Imagen
```bash
docker build -t notifications-service .
```

### Ejecutar Servicio
```bash
docker-compose up notifications-service
```

### Ejecutar Worker
```bash
docker-compose up celery-worker
```

## 🧪 Pruebas

### Probar Envío de Email
```bash
curl -X POST http://localhost:8004/api/notifications/email \
  -H "Content-Type: application/json" \
  -d '{
    "to_emails": ["test@example.com"],
    "subject": "Test Email",
    "html_body": "<h1>Test</h1><p>This is a test email</p>"
  }'
```

### Probar Confirmación de Reserva
```bash
curl -X POST http://localhost:8004/api/notifications/reservation/confirmation \
  -H "Content-Type: application/json" \
  -d '{
    "user_email": "user@example.com",
    "user_name": "Test User",
    "reservation_data": {
      "id": 123,
      "date": "2025-11-10",
      "time": "10:00",
      "service": "Test Service",
      "location": "Test Location"
    }
  }'
```

## 📊 Logs

Los logs se generan en formato estructurado con información sobre:
- Emails encolados
- Tareas ejecutadas
- Errores y reintentos
- Estado de Redis/Celery

## 🔒 Seguridad

- Las contraseñas SMTP deben estar en variables de entorno
- Los templates sanitizan HTML automáticamente
- Límite de destinatarios por email (configurable)
- Timeout en envíos para evitar bloqueos

## 🚨 Manejo de Errores

El servicio implementa:
- **Reintentos automáticos**: 3 intentos por defecto
- **Delay exponencial**: Entre reintentos
- **Logging detallado**: Para debugging
- **Circuit breaker**: Para evitar cascadas de fallos

## 📈 Escalabilidad

Para escalar el servicio:

1. **Múltiples Workers**: Aumentar `--concurrency` o ejecutar más contenedores
2. **Redis Cluster**: Para alta disponibilidad
3. **Load Balancer**: Múltiples instancias del servicio API
4. **Monitoreo**: Usar Flower para Celery

```bash
# Flower - Interfaz web para monitorear Celery
celery -A celery_config flower --port=5555
```

## 🔗 Integración con Otros Servicios

### Desde Servicio de Reservas
```python
import httpx

# Enviar confirmación
async def send_confirmation(reservation_data):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://notifications-service:8004/api/notifications/reservation/confirmation",
            json={
                "user_email": reservation_data["user_email"],
                "user_name": reservation_data["user_name"],
                "reservation_data": reservation_data
            }
        )
        return response.json()
```

### Desde Servicio de Documentos
```python
# Notificar documento subido
async def notify_document_upload(user_data, document_data):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://notifications-service:8004/api/notifications/document",
            json={
                "user_email": user_data["email"],
                "user_name": user_data["name"],
                "document_data": document_data,
                "notification_type": "uploaded"
            }
        )
        return response.json()
```

## 📝 TODO / Mejoras Futuras

- [ ] Soporte para SMS (Twilio)
- [ ] Notificaciones Push
- [ ] Webhooks
- [ ] Rate limiting por usuario
- [ ] Dashboard de analytics
- [ ] Plantillas personalizables por usuario
- [ ] Soporte multi-idioma
- [ ] Firma digital de emails (DKIM)

## 🤝 Contribución

Para contribuir al servicio:

1. Agrega nuevas tareas en `tasks.py`
2. Crea templates HTML en `templates/`
3. Documenta endpoints en este README
4. Prueba con diferentes proveedores SMTP

## 📄 Licencia

Proyecto académico - Universidad 2025
