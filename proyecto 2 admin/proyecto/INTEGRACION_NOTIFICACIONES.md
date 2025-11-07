# Integración del Sistema de Notificaciones

## 📋 Resumen de Integración

Este documento resume la integración completa del sistema de notificaciones por email con todos los servicios del sistema municipal.

## 🎯 Servicios Integrados

### 1. **Servicio de Autenticación (auth-service)**

#### Modificaciones realizadas:
- ✅ Agregado `httpx==0.27.2` a `requirements.txt`
- ✅ Importado `httpx` y `logging` en `main.py`
- ✅ Creada función helper `send_notification()` para envío async no bloqueante
- ✅ Modificado endpoint `POST /register` para enviar email de bienvenida
- ✅ Implementado endpoint `POST /password-reset/request` para solicitar reset
- ✅ Implementado endpoint `POST /password-reset/confirm` para confirmar reset

#### Emails enviados:
- **Welcome Email**: Se envía automáticamente al registrar un nuevo usuario
  - Tipo: `welcome`
  - Datos: `user_name`, `email`, `registration_date`
  
- **Password Reset Email**: Se envía cuando el usuario solicita recuperar contraseña
  - Tipo: `password_reset`
  - Datos: `user_name`, `reset_link`, `expiry_time`

#### Endpoints nuevos:
```
POST /password-reset/request
Body: { "email": "user@example.com" }
Response: { "message": "Email enviado si el usuario existe" }

POST /password-reset/confirm
Body: { "token": "...", "new_password": "..." }
Response: { "message": "Contraseña actualizada exitosamente" }
```

---

### 2. **Servicio de Reservaciones (reservations-service)**

#### Modificaciones realizadas:
- ✅ Agregado `httpx==0.27.2` a `requirements.txt`
- ✅ Importado `httpx` y `logging` en `main.py`
- ✅ Creada función helper `send_notification()` para envío async no bloqueante
- ✅ Modificado endpoint `POST /reservations` (ahora async)
- ✅ Modificado endpoint `DELETE /reservations/{reservation_id}` (ahora async)

#### Emails enviados:
- **Confirmation Email**: Se envía al crear una nueva reservación
  - Tipo: `confirmation`
  - Datos: `user_name`, `facility_name`, `reservation_date`, `start_time`, `end_time`, `reservation_id`
  
- **Cancellation Email**: Se envía al cancelar una reservación existente
  - Tipo: `cancellation`
  - Datos: `user_name`, `facility_name`, `reservation_date`, `cancellation_date`, `reservation_id`

---

### 3. **Servicio de Documentos (documents-services)**

#### Modificaciones realizadas:
- ✅ Agregado `httpx==0.27.2` a `requirements.txt`
- ✅ Importado `httpx` y `logging` en `main.py`
- ✅ Creada función helper `send_notification()` para envío async no bloqueante
- ✅ Modificado endpoint `POST /upload` para aceptar header `x-user-email`
- ✅ Agregado envío de notificación después de subir documento

#### Emails enviados:
- **Document Upload Email**: Se envía al subir un documento exitosamente
  - Tipo: `document`
  - Datos: `user_name`, `document_name`, `document_type`, `status`, `upload_date`

#### Nota importante:
El endpoint `/upload` ahora acepta un header adicional:
```
x-user-email: user@example.com
```
Este header es opcional pero necesario para enviar la notificación por email.

---

## 🚀 API Gateway

### Configuración en nginx.conf:
```nginx
upstream notifications_cluster {
    server notifications-service:8004;
}

location /api/notifications/ {
    proxy_pass http://notifications_cluster/;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
    proxy_cache_bypass $http_upgrade;
}
```

Todas las peticiones a `/api/notifications/` se redirigen al servicio de notificaciones.

---

## 💻 Frontend

### Cliente API creado:
**Archivo**: `services/frontend/src/services/notificationsAPI.js`

#### Métodos disponibles:
```javascript
// Enviar notificaciones
sendReservationConfirmation(data)
sendReservationReminder(data)
sendReservationCancellation(data)
sendDocumentNotification(data)
sendWelcomeEmail(data)
sendPasswordReset(data)
sendCustomNotification(data)

// Monitoreo
getTaskStatus(taskId)
getNotificationHistory(params)
```

### Modificaciones en componentes:
- **Reservas.jsx**: Actualizado con mensajes que mencionan que se enviarán emails de confirmación/cancelación

---

## 🐳 Docker

### Servicios agregados en docker-compose.yml:

```yaml
redis:
  image: redis:7-alpine
  ports: ["6379:6379"]
  volumes: [redis_data:/data]

notifications-service:
  build: ./services/notificacion-service
  ports: ["8004:8004"]
  depends_on: [redis]
  environment:
    - SMTP_HOST=${SMTP_HOST}
    - SMTP_PORT=${SMTP_PORT}
    - SMTP_USERNAME=${SMTP_USERNAME}
    - SMTP_PASSWORD=${SMTP_PASSWORD}
    - SMTP_FROM_EMAIL=${SMTP_FROM_EMAIL}
    - REDIS_HOST=redis
    - REDIS_PORT=6379

celery-worker:
  build: ./services/notificacion-service
  command: celery -A celery_config worker --loglevel=info
  depends_on: [redis, notifications-service]
  environment: [same as notifications-service]
```

---

## 📝 Tipos de Email Disponibles

| Tipo | Plantilla | Disparador | Servicio |
|------|-----------|-----------|----------|
| `welcome` | welcome.html | Registro de usuario | auth-service |
| `password_reset` | password_reset.html | Solicitud de reset | auth-service |
| `confirmation` | confirmation.html | Crear reservación | reservations-service |
| `reminder` | reminder.html | Manual/Scheduled | - |
| `cancellation` | cancellation.html | Cancelar reservación | reservations-service |
| `document` | document.html | Subir documento | documents-services |

---

## 🔧 Configuración Requerida

### Variables de entorno (.env):
```bash
# SMTP Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=Sistema Municipal <noreply@municipal.gov>

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
```

Para Gmail, necesitas:
1. Habilitar "Verificación en 2 pasos"
2. Generar una "Contraseña de aplicación"
3. Usar esa contraseña en `SMTP_PASSWORD`

---

## 📊 Patrón de Integración

Todos los servicios siguen el mismo patrón para enviar notificaciones:

```python
import httpx
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def send_notification(notification_type: str, recipient_email: str, data: dict):
    """Envía notificación de forma no bloqueante"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                "http://notifications-service:8004/notifications/send",
                json={
                    "notification_type": notification_type,
                    "recipient_email": recipient_email,
                    "data": data
                }
            )
            logger.info(f"Notificación enviada: {notification_type} a {recipient_email}")
    except Exception as e:
        logger.error(f"Error enviando notificación: {str(e)}")
        # No propagamos el error para no afectar el flujo principal
```

### Características clave:
- ✅ **No bloqueante**: Usa `async/await`
- ✅ **Timeout corto**: 5 segundos máximo
- ✅ **Error handling**: Los errores se loguean pero no detienen el proceso
- ✅ **Fire-and-forget**: El servicio principal continúa independientemente del resultado

---

## 🧪 Pruebas

### Script de prueba: `test_notifications.ps1`

```powershell
# Prueba todos los tipos de notificaciones
.\test_notifications.ps1
```

### Pruebas manuales:
```bash
# 1. Registrar usuario (debe enviar welcome email)
POST http://localhost/api/auth/register
Body: {"email": "test@example.com", "password": "test123", "name": "Test User"}

# 2. Crear reservación (debe enviar confirmation email)
POST http://localhost/api/reservations
Body: {"facility_id": 1, "date": "2024-01-20", "start_time": "10:00", ...}

# 3. Subir documento (debe enviar document email)
POST http://localhost/api/documents/upload
Headers: {"x-user-email": "test@example.com"}
Form-data: file, document_type, etc.

# 4. Solicitar password reset
POST http://localhost/api/auth/password-reset/request
Body: {"email": "test@example.com"}
```

---

## ✅ Checklist de Implementación

### Backend:
- [x] Servicio de notificaciones creado (FastAPI + Celery + Redis)
- [x] 6 plantillas HTML de email diseñadas
- [x] API Gateway configurado
- [x] Auth service integrado (welcome + password reset)
- [x] Reservations service integrado (confirmation + cancellation)
- [x] Documents service integrado (upload notification)
- [x] Docker compose actualizado
- [x] Dependencias agregadas (httpx en todos los servicios)

### Frontend:
- [x] Cliente API de notificaciones creado
- [x] Mensajes actualizados en Reservas.jsx
- [ ] Frontend para password reset (pendiente)
- [ ] Mensajes de bienvenida en Register.jsx (pendiente)

### Testing:
- [x] Script de prueba PowerShell creado
- [ ] Pruebas end-to-end realizadas (pendiente)
- [ ] Configuración SMTP en producción (pendiente)

---

## 📚 Documentación Adicional

- **README.md**: Descripción general del servicio de notificaciones
- **IMPLEMENTACION.md**: Guía detallada de implementación técnica
- **INTEGRACION.md**: Guía de integración con otros servicios
- **INTEGRACION_NOTIFICACIONES.md**: Este documento (resumen de integración completa)

---

## 🚦 Próximos Pasos

1. **Testing Completo**:
   - Iniciar Docker: `docker-compose up -d`
   - Ejecutar tests: `.\test_notifications.ps1`
   - Verificar emails recibidos

2. **Frontend Password Reset**:
   - Crear componente `ForgotPassword.jsx`
   - Crear componente `ResetPassword.jsx`
   - Integrar en el routing

3. **Frontend Welcome Messages**:
   - Actualizar `Register.jsx` para mostrar mensaje de email enviado
   - Agregar instrucciones de verificación de correo

4. **Configuración Producción**:
   - Configurar SMTP real (no Gmail de prueba)
   - Ajustar timeouts y retries según necesidad
   - Configurar monitoreo de cola Redis
   - Configurar logs de Celery

5. **Mejoras Opcionales**:
   - Agregar template de email para documentos aprobados/rechazados
   - Implementar sistema de preferencias de notificaciones
   - Agregar notificaciones por SMS (opcional)
   - Dashboard de historial de notificaciones

---

## 📞 Soporte

Para cualquier duda sobre la integración, revisar:
1. Logs del servicio: `docker-compose logs notifications-service`
2. Logs de Celery: `docker-compose logs celery-worker`
3. Estado de Redis: `docker-compose exec redis redis-cli monitor`
4. Logs de servicios individuales: `docker-compose logs auth-service` / `reservations-service` / `documents-services`

---

**Fecha de integración**: 2024-01-XX  
**Versión**: 1.0.0  
**Estado**: ✅ Integración Backend Completa | ⏳ Frontend Parcial
