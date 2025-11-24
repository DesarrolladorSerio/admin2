# 📧 Servicio de Notificaciones - Resumen de Implementación

## ✅ Lo que se ha implementado

### 1. **Arquitectura del Servicio**
- **FastAPI** como servidor API
- **Celery** para procesamiento asíncrono de tareas
- **Redis** como broker de mensajes y backend de resultados
- **aiosmtplib** para envío asíncrono de emails
- **Jinja2** para templates HTML profesionales

### 2. **Archivos Creados**

```
notificacion-service/
├── Dockerfile              # Imagen Docker del servicio
├── requirements.txt        # Dependencias Python
├── config.py              # Configuración centralizada
├── main.py                # API FastAPI con endpoints
├── celery_config.py       # Configuración de Celery
├── tasks.py               # Tareas asíncronas de Celery
├── email_service.py       # Lógica de envío de emails
├── README.md              # Documentación completa
├── .env.example           # Ejemplo de variables de entorno
└── templates/             # Templates HTML para emails
    ├── reservation_confirmation.html
    ├── reservation_reminder.html
    ├── reservation_cancellation.html
    ├── document_notification.html
    ├── welcome.html
    └── password_reset.html
```

### 3. **Funcionalidades Implementadas**

#### ✉️ Tipos de Notificaciones
1. **Email genérico** - Envío flexible con HTML/texto
2. **Confirmación de reserva** - Al crear una reserva
3. **Recordatorio de reserva** - 24h antes del evento
4. **Cancelación de reserva** - Al cancelar una reserva
5. **Notificación de documento** - Al subir/aprobar/rechazar documentos
6. **Email de bienvenida** - Al registrar nuevo usuario
7. **Recuperación de contraseña** - Para reset de password
8. **Envío en lote** - Múltiples emails simultáneos

#### 🔄 Sistema de Cola
- **Procesamiento asíncrono** - No bloquea la API
- **Reintentos automáticos** - 3 intentos con delay exponencial
- **Monitoreo de tareas** - Consultar estado por task_id
- **Escalabilidad** - Múltiples workers en paralelo

#### 🎨 Templates HTML
- **Diseño profesional** - Responsive y atractivo
- **Variables dinámicas** - Personalización por usuario
- **Consistencia visual** - Mismo estilo en todos los emails

### 4. **Endpoints Disponibles**

```bash
# Health check
GET  /health
GET  /

# Notificaciones
POST /api/notifications/email                        # Email genérico
POST /api/notifications/reservation/confirmation     # Confirmación reserva
POST /api/notifications/reservation/reminder         # Recordatorio reserva
POST /api/notifications/reservation/cancellation     # Cancelación reserva
POST /api/notifications/document                     # Notificación documento
POST /api/notifications/welcome                      # Bienvenida
POST /api/notifications/password-reset               # Reset password
POST /api/notifications/batch                        # Envío en lote

# Monitoreo
GET  /api/notifications/task/{task_id}               # Estado de tarea
GET  /api/notifications/stats                        # Estadísticas
```

### 5. **Configuración Docker**

#### Servicios agregados a docker-compose.yml:
- **redis** - Sistema de cola (puerto 6379)
- **notifications-service** - API FastAPI (puerto 8004)
- **celery-worker** - Worker para procesar emails

#### Volumen agregado:
- **redis_data** - Persistencia de datos de Redis

### 6. **Variables de Entorno Requeridas**

```env
# SMTP (IMPORTANTE: Configurar antes de usar)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu-email@gmail.com          # ⚠️ CONFIGURAR
SMTP_PASSWORD=tu-app-password          # ⚠️ CONFIGURAR
SMTP_FROM_EMAIL=noreply@sistema.com
SMTP_FROM_NAME=Sistema de Reservas

# Redis y Celery (ya configurado)
REDIS_HOST=redis
REDIS_PORT=6379
CELERY_BROKER_URL=redis://redis:6379/0

# Puerto del servicio
NOTIFICATIONS_SERVICE_PORT=8004
```

## 🚀 Cómo Usar el Servicio

### Paso 1: Configurar SMTP

Para Gmail (recomendado para testing):
1. Ve a tu cuenta de Google
2. Habilita verificación en 2 pasos
3. Ve a https://myaccount.google.com/apppasswords
4. Crea una "Contraseña de aplicación"
5. Agrega las credenciales en `.env`:
   ```env
   SMTP_USER=tu-email@gmail.com
   SMTP_PASSWORD=xxxx-xxxx-xxxx-xxxx
   ```

### Paso 2: Levantar los Servicios

```bash
# Levantar todo el stack
docker-compose up -d

# O solo los servicios de notificaciones
docker-compose up -d redis notifications-service celery-worker
```

### Paso 3: Verificar que funciona

```bash
# 1. Verificar health
curl http://localhost:8004/health

# 2. Enviar email de prueba
curl -X POST http://localhost:8004/api/notifications/email \
  -H "Content-Type: application/json" \
  -d '{
    "to_emails": ["tu-email@gmail.com"],
    "subject": "Test desde Notifications Service",
    "html_body": "<h1>¡Funciona!</h1><p>El servicio está operativo</p>"
  }'

# 3. Verificar estado de la tarea (usar el task_id de la respuesta)
curl http://localhost:8004/api/notifications/task/{task_id}
```

## 🔗 Integración con Otros Servicios

### Desde Servicio de Reservas (main.py)

```python
import httpx

async def create_reservation_handler(reservation_data, user_data):
    # ... crear reserva en DB ...
    
    # Enviar confirmación por email
    async with httpx.AsyncClient() as client:
        try:
            await client.post(
                "http://notifications-service:8004/api/notifications/reservation/confirmation",
                json={
                    "user_email": user_data["email"],
                    "user_name": user_data["name"],
                    "reservation_data": {
                        "id": reservation.id,
                        "date": str(reservation.date),
                        "time": str(reservation.time),
                        "service": reservation.service_name,
                        "location": reservation.location
                    }
                },
                timeout=5.0
            )
        except Exception as e:
            # Log error pero no falla la reserva
            logger.error(f"Error enviando notificación: {e}")
```

### Desde Servicio de Documentos (main.py)

```python
async def upload_document_handler(document_data, user_data):
    # ... guardar documento en MinIO y DB ...
    
    # Notificar documento subido
    async with httpx.AsyncClient() as client:
        try:
            await client.post(
                "http://notifications-service:8004/api/notifications/document",
                json={
                    "user_email": user_data["email"],
                    "user_name": user_data["name"],
                    "document_data": {
                        "name": document.original_filename,
                        "type": document.document_type,
                        "upload_date": str(document.created_at)
                    },
                    "notification_type": "uploaded"
                },
                timeout=5.0
            )
        except Exception as e:
            logger.error(f"Error enviando notificación: {e}")
```

### Desde Servicio de Auth (main.py)

```python
async def register_user_handler(user_data):
    # ... crear usuario en DB ...
    
    # Enviar email de bienvenida
    async with httpx.AsyncClient() as client:
        try:
            await client.post(
                "http://notifications-service:8004/api/notifications/welcome",
                json={
                    "user_email": user_data["email"],
                    "user_name": user_data["name"],
                    "temp_password": temp_password if temp_password else None
                },
                timeout=5.0
            )
        except Exception as e:
            logger.error(f"Error enviando bienvenida: {e}")
```

## 📊 Monitoreo y Debugging

### Ver logs del servicio
```bash
docker-compose logs -f notifications-service
```

### Ver logs del worker
```bash
docker-compose logs -f celery-worker
```

### Ver tareas en Redis
```bash
docker exec -it redis_queue redis-cli
> KEYS *
> GET celery-task-meta-{task_id}
```

### Estadísticas del servicio
```bash
curl http://localhost:8004/api/notifications/stats
```

## ⚠️ Notas Importantes

### ❌ NO Necesita Base de Datos Propia
El servicio de notificaciones **NO requiere su propia base de datos** porque:
- Las notificaciones son efímeras (se envían y listo)
- Redis maneja la cola temporalmente
- Los datos vienen de otros servicios (auth, reservations, documents)

### ✅ Ventajas de esta Arquitectura
1. **Desacoplamiento** - Los servicios no se bloquean esperando emails
2. **Resiliencia** - Reintentos automáticos si falla el SMTP
3. **Escalabilidad** - Agregar más workers es trivial
4. **Monitoreo** - Estado de cada tarea es consultable
5. **Performance** - No bloquea las operaciones principales

### 🔒 Seguridad
- Nunca commitear `SMTP_USER` y `SMTP_PASSWORD` al repo
- Usar contraseñas de aplicación, no la contraseña real de email
- Los templates sanitizan HTML automáticamente
- Límite de 50 destinatarios por email por defecto

## 📈 Próximos Pasos (Opcional)

Si quieres mejorar el servicio en el futuro:

1. **Programar recordatorios automáticos**
   - Usar Celery Beat para tareas periódicas
   - Buscar reservas del día siguiente
   - Enviar recordatorios 24h antes

2. **Dashboard de monitoreo**
   - Instalar Flower: `pip install flower`
   - Ver tareas en tiempo real en http://localhost:5555

3. **Rate limiting**
   - Limitar emails por usuario/hora
   - Prevenir spam

4. **Multi-canal**
   - SMS con Twilio
   - Notificaciones push
   - Webhooks

5. **Analytics**
   - Tasas de apertura de emails
   - Clicks en enlaces
   - Rebotes

## 🎯 Resumen Ejecutivo

### ¿Qué se implementó?
✅ Servicio completo de notificaciones con email + cola

### ¿Necesita DB?
❌ NO - Usa Redis para cola, no almacena datos

### ¿Qué falta configurar?
⚠️ Solo las credenciales SMTP en `.env`:
- `SMTP_USER`
- `SMTP_PASSWORD`

### ¿Está listo para producción?
✅ Sí, con las siguientes consideraciones:
- Configurar SMTP con credenciales reales
- Ajustar límites según necesidad
- Monitorear con Flower (opcional)
- Configurar alertas si falla Redis

### ¿Cómo probarlo?
```bash
# 1. Configurar SMTP en .env
# 2. Levantar servicios
docker-compose up -d redis notifications-service celery-worker

# 3. Enviar prueba
curl -X POST http://localhost:8004/api/notifications/email \
  -H "Content-Type: application/json" \
  -d '{"to_emails":["tu@email.com"],"subject":"Test","html_body":"<h1>Test</h1>"}'
```

## 📚 Documentación Adicional

- **README completo**: `services/notificacion-service/README.md`
- **Ejemplo .env**: `services/notificacion-service/.env.example`
- **Templates HTML**: `services/notificacion-service/templates/`

---

**¡El servicio está completo y listo para usar!** 🎉

Solo necesitas configurar las credenciales SMTP y podrás enviar notificaciones desde cualquier otro servicio del sistema.
