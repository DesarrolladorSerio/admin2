# 🧪 GUÍA COMPLETA DE PRUEBAS - SISTEMA MUNICIPAL DE RESERVACIONES

**Fecha:** 9 de Noviembre de 2025  
**Versión:** 1.0.0  
**Estado:** ✅ Todos los servicios operativos

---

## 📋 ÍNDICE DE SERVICIOS

1. [Frontend - Interfaz de Usuario](#1-frontend---interfaz-de-usuario)
2. [API Gateway - Punto de Entrada Único](#2-api-gateway---punto-de-entrada-único)
3. [Servicio de Autenticación](#3-servicio-de-autenticación)
4. [Servicio de Reservaciones](#4-servicio-de-reservaciones)
5. [Servicio de Documentos](#5-servicio-de-documentos)
6. [Servicio de Notificaciones](#6-servicio-de-notificaciones)
7. [ChatBot IA (100% Gratuito)](#7-chatbot-ia-100-gratuito)
8. [Bases de Datos PostgreSQL](#8-bases-de-datos-postgresql)
9. [Almacenamiento MinIO](#9-almacenamiento-minio)
10. [Sistema de Monitoreo](#10-sistema-de-monitoreo)
11. [Redis Cache](#11-redis-cache)
12. [Backups Automáticos](#12-backups-automáticos)

---

## 1. FRONTEND - Interfaz de Usuario

### 🌐 Acceso
- **URL:** http://localhost:3000
- **Puerto:** 3000
- **Tecnología:** React + Vite + TailwindCSS
- **Estado:** ✅ Healthy

### 🧪 Pruebas a Realizar

#### 1.1 Acceso a la Aplicación
```bash
# Abrir en navegador
http://localhost:3000
```
**Verificar:**
- [ ] La página carga correctamente
- [ ] Se muestra el formulario de login
- [ ] Diseño responsive funciona en móvil/tablet/desktop
- [ ] No hay errores en la consola del navegador (F12)

#### 1.2 Registro de Usuario
**Pasos:**
1. Click en "Registrarse" o "Crear cuenta"
2. Completar formulario:
   - Nombre completo
   - Email válido
   - Contraseña (mínimo 8 caracteres, mayúscula, minúscula, número)
   - Confirmar contraseña
3. Click en "Registrar"

**Verificar:**
- [ ] Validación de formulario funciona
- [ ] Se crea el usuario correctamente
- [ ] Recibes email de bienvenida (revisar correo)
- [ ] Redirección al login

#### 1.3 Login de Usuario
**Pasos:**
1. Ingresar email registrado
2. Ingresar contraseña
3. Click en "Iniciar Sesión"

**Verificar:**
- [ ] Login exitoso
- [ ] Se guarda token en localStorage
- [ ] Redirección al dashboard
- [ ] Menú de navegación visible

#### 1.4 Dashboard Principal
**Verificar:**
- [ ] Visualización de estadísticas
- [ ] Menú lateral con opciones:
  - Reservaciones
  - Mis Reservas
  - Documentos
  - Chat de Ayuda
  - Perfil
- [ ] Botón de ChatBot visible (esquina inferior derecha)

#### 1.5 Módulo de Reservaciones
**Pruebas:**
1. **Ver Disponibilidad**
   - [ ] Calendario muestra fechas disponibles
   - [ ] Horarios se cargan correctamente
   - [ ] Filtros por tipo de licencia funcionan

2. **Crear Reservación**
   - [ ] Seleccionar fecha
   - [ ] Seleccionar hora
   - [ ] Seleccionar tipo de licencia
   - [ ] Agregar notas (opcional)
   - [ ] Click en "Reservar"
   - [ ] Confirmación exitosa
   - [ ] Email de confirmación recibido

3. **Ver Mis Reservas**
   - [ ] Lista de reservas activas
   - [ ] Filtrar por estado (pendiente/confirmada/completada/cancelada)
   - [ ] Ver detalles de cada reserva

4. **Cancelar Reservación**
   - [ ] Click en "Cancelar" en una reserva
   - [ ] Confirmar cancelación
   - [ ] Estado cambia a "Cancelada"
   - [ ] Email de cancelación recibido

#### 1.6 Módulo de Documentos
**Pruebas:**
1. **Subir Documento**
   - [ ] Click en "Subir Archivo"
   - [ ] Seleccionar archivo (PDF, JPG, PNG)
   - [ ] Agregar descripción
   - [ ] Upload exitoso
   - [ ] Documento aparece en lista

2. **Ver Documentos**
   - [ ] Lista de documentos cargados
   - [ ] Previsualización funciona
   - [ ] Información de tamaño y fecha

3. **Descargar Documento**
   - [ ] Click en "Descargar"
   - [ ] Archivo se descarga correctamente

4. **Eliminar Documento**
   - [ ] Click en "Eliminar"
   - [ ] Confirmar eliminación
   - [ ] Documento removido de la lista

#### 1.7 ChatBot de Ayuda
**Pruebas:**
1. Click en botón flotante del ChatBot (esquina inferior derecha)
2. **Preguntas de Prueba:**
   ```
   - "Hola, ¿cómo puedo hacer una reservación?"
   - "¿Cuáles son los horarios disponibles?"
   - "¿Qué tipos de licencias puedo tramitar?"
   - "¿Cómo cancelo una reserva?"
   - "¿Qué documentos necesito?"
   ```

**Verificar:**
- [ ] ChatBot responde en español
- [ ] Respuestas coherentes y útiles
- [ ] Historial de chat se mantiene
- [ ] Puede cerrar y reabrir sin perder contexto
- [ ] Botón "Limpiar Chat" funciona

---

## 2. API GATEWAY - Punto de Entrada Único

### 🌐 Acceso
- **URL:** http://localhost:80
- **Puerto:** 80
- **Tecnología:** Nginx
- **Estado:** ✅ Healthy

### 🧪 Pruebas a Realizar

#### 2.1 Enrutamiento de APIs
```bash
# Probar enrutamiento a Auth Service
curl http://localhost/api/auth/health

# Probar enrutamiento a Reservations Service
curl http://localhost/api/reservations/health

# Probar enrutamiento a Documents Service
curl http://localhost/api/documents/health

# Probar enrutamiento a Notifications Service
curl http://localhost/api/notifications/health

# Probar enrutamiento a ChatBot Service
curl http://localhost/api/chatbot/health
```

**Verificar:**
- [ ] Todos devuelven status 200
- [ ] Respuesta JSON válida
- [ ] Tiempo de respuesta < 500ms

#### 2.2 Balanceo de Carga
El gateway distribuye peticiones entre múltiples instancias:
- Auth: 2 instancias
- Reservations: 2 instancias
- ChatBot: 2 instancias

**Verificar:**
- [ ] Logs muestran distribución de carga
- [ ] Si cae una instancia, la otra responde

#### 2.3 Headers CORS
```bash
curl -i -X OPTIONS http://localhost/api/auth/health \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST"
```

**Verificar:**
- [ ] Header Access-Control-Allow-Origin presente
- [ ] Header Access-Control-Allow-Methods presente

---

## 3. SERVICIO DE AUTENTICACIÓN

### 🌐 Acceso Directo
- **URL:** http://localhost:8000
- **Puerto:** 8000
- **Instancias:** 2 (auth_service_1, auth_service_2)
- **Estado:** ✅ Healthy

### 🧪 Pruebas con PowerShell

#### 3.1 Health Check
```powershell
Invoke-WebRequest -Uri http://localhost:8000/health -Method GET
```
**Esperado:** Status 200, JSON con `{"status":"ok"}`

#### 3.2 Registro de Usuario
```powershell
$body = @{
    username = "testuser"
    email = "test@example.com"
    password = "Test1234!"
    full_name = "Usuario de Prueba"
} | ConvertTo-Json

Invoke-WebRequest -Uri http://localhost:8000/register -Method POST -Body $body -ContentType "application/json"
```

**Verificar:**
- [ ] Status 200 o 201
- [ ] Respuesta contiene user_id
- [ ] Email de bienvenida enviado

#### 3.3 Login
```powershell
$body = @{
    username = "testuser"
    password = "Test1234!"
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri http://localhost:8000/login -Method POST -Body $body -ContentType "application/json"
$token = ($response.Content | ConvertFrom-Json).access_token
Write-Host "Token: $token"
```

**Verificar:**
- [ ] Status 200
- [ ] Respuesta contiene access_token
- [ ] Token es un JWT válido

#### 3.4 Obtener Perfil (con token)
```powershell
$headers = @{
    Authorization = "Bearer $token"
}

Invoke-WebRequest -Uri http://localhost:8000/me -Method GET -Headers $headers
```

**Verificar:**
- [ ] Status 200
- [ ] Respuesta contiene datos del usuario
- [ ] No incluye password

#### 3.5 Cambio de Contraseña
```powershell
$body = @{
    old_password = "Test1234!"
    new_password = "NewPass1234!"
} | ConvertTo-Json

$headers = @{
    Authorization = "Bearer $token"
}

Invoke-WebRequest -Uri http://localhost:8000/change-password -Method POST -Body $body -ContentType "application/json" -Headers $headers
```

**Verificar:**
- [ ] Status 200
- [ ] Mensaje de confirmación
- [ ] Nuevo login con nueva contraseña funciona

---

## 4. SERVICIO DE RESERVACIONES

### 🌐 Acceso Directo
- **URL:** http://localhost:8002
- **Puerto:** 8002
- **Instancias:** 2 (reservations_service_1, reservations_service_2)
- **Estado:** ✅ Healthy

### 🧪 Pruebas con PowerShell

#### 4.1 Health Check
```powershell
Invoke-WebRequest -Uri http://localhost:8002/health -Method GET
```

#### 4.2 Ver Disponibilidad de Horarios
```powershell
$headers = @{
    Authorization = "Bearer $token"
}

Invoke-WebRequest -Uri "http://localhost:8002/availability?date=2025-11-10" -Method GET -Headers $headers
```

**Verificar:**
- [ ] Status 200
- [ ] Lista de horarios disponibles
- [ ] Formato de fecha correcto

#### 4.3 Crear Reservación
```powershell
$body = @{
    license_type = "Conducir"
    reservation_date = "2025-11-15"
    reservation_time = "09:00"
    notes = "Renovación de licencia"
} | ConvertTo-Json

$headers = @{
    Authorization = "Bearer $token"
}

Invoke-WebRequest -Uri http://localhost:8002/reservations -Method POST -Body $body -ContentType "application/json" -Headers $headers
```

**Verificar:**
- [ ] Status 201
- [ ] Respuesta con reservation_id
- [ ] Email de confirmación enviado
- [ ] Estado inicial: "pendiente"

#### 4.4 Listar Mis Reservaciones
```powershell
$headers = @{
    Authorization = "Bearer $token"
}

Invoke-WebRequest -Uri http://localhost:8002/reservations/my -Method GET -Headers $headers
```

**Verificar:**
- [ ] Status 200
- [ ] Array de reservaciones
- [ ] Solo muestra reservas del usuario actual

#### 4.5 Obtener Detalles de Reservación
```powershell
$reservationId = 1  # ID obtenido del paso anterior

$headers = @{
    Authorization = "Bearer $token"
}

Invoke-WebRequest -Uri "http://localhost:8002/reservations/$reservationId" -Method GET -Headers $headers
```

**Verificar:**
- [ ] Status 200
- [ ] Detalles completos de la reserva
- [ ] Incluye información del usuario

#### 4.6 Actualizar Estado de Reservación
```powershell
$body = @{
    status = "confirmada"
} | ConvertTo-Json

$headers = @{
    Authorization = "Bearer $token"
}

Invoke-WebRequest -Uri "http://localhost:8002/reservations/$reservationId/status" -Method PATCH -Body $body -ContentType "application/json" -Headers $headers
```

**Verificar:**
- [ ] Status 200
- [ ] Estado actualizado
- [ ] Email de notificación enviado

#### 4.7 Cancelar Reservación
```powershell
$headers = @{
    Authorization = "Bearer $token"
}

Invoke-WebRequest -Uri "http://localhost:8002/reservations/$reservationId/cancel" -Method POST -Headers $headers
```

**Verificar:**
- [ ] Status 200
- [ ] Estado cambia a "cancelada"
- [ ] Email de cancelación enviado
- [ ] Horario queda disponible nuevamente

#### 4.8 Validación de Conflictos
Intentar crear dos reservas en el mismo horario:

```powershell
# Primera reserva
$body1 = @{
    license_type = "Conducir"
    reservation_date = "2025-11-20"
    reservation_time = "10:00"
} | ConvertTo-Json

Invoke-WebRequest -Uri http://localhost:8002/reservations -Method POST -Body $body1 -ContentType "application/json" -Headers $headers

# Segunda reserva (mismo horario) - DEBE FALLAR
$body2 = @{
    license_type = "Moto"
    reservation_date = "2025-11-20"
    reservation_time = "10:00"
} | ConvertTo-Json

Invoke-WebRequest -Uri http://localhost:8002/reservations -Method POST -Body $body2 -ContentType "application/json" -Headers $headers
```

**Verificar:**
- [ ] Primera reserva: Status 201 (éxito)
- [ ] Segunda reserva: Status 409 o 400 (conflicto)
- [ ] Mensaje de error claro

---

## 5. SERVICIO DE DOCUMENTOS

### 🌐 Acceso Directo
- **URL:** http://localhost:8003
- **Puerto:** 8003
- **Estado:** ✅ Healthy

### 🧪 Pruebas con PowerShell

#### 5.1 Health Check
```powershell
Invoke-WebRequest -Uri http://localhost:8003/health -Method GET
```

#### 5.2 Subir Documento
```powershell
$headers = @{
    Authorization = "Bearer $token"
}

# Crear archivo de prueba
"Contenido de prueba" | Out-File -FilePath "test_document.txt"

# Subir archivo
$form = @{
    file = Get-Item -Path "test_document.txt"
    description = "Documento de prueba"
    document_type = "identificacion"
}

Invoke-WebRequest -Uri http://localhost:8003/documents/upload -Method POST -Form $form -Headers $headers
```

**Verificar:**
- [ ] Status 201
- [ ] Respuesta con document_id
- [ ] Archivo guardado en MinIO
- [ ] Metadata guardada en PostgreSQL

#### 5.3 Listar Mis Documentos
```powershell
$headers = @{
    Authorization = "Bearer $token"
}

Invoke-WebRequest -Uri http://localhost:8003/documents/my -Method GET -Headers $headers
```

**Verificar:**
- [ ] Status 200
- [ ] Lista de documentos del usuario
- [ ] Información: nombre, tamaño, fecha, tipo

#### 5.4 Descargar Documento
```powershell
$documentId = 1  # ID del documento

$headers = @{
    Authorization = "Bearer $token"
}

Invoke-WebRequest -Uri "http://localhost:8003/documents/$documentId/download" -Method GET -Headers $headers -OutFile "downloaded_document.txt"
```

**Verificar:**
- [ ] Status 200
- [ ] Archivo descargado correctamente
- [ ] Contenido coincide con el original

#### 5.5 Eliminar Documento
```powershell
$headers = @{
    Authorization = "Bearer $token"
}

Invoke-WebRequest -Uri "http://localhost:8003/documents/$documentId" -Method DELETE -Headers $headers
```

**Verificar:**
- [ ] Status 200 o 204
- [ ] Documento removido de la base de datos
- [ ] Archivo eliminado de MinIO

---

## 6. SERVICIO DE NOTIFICACIONES

### 🌐 Acceso Directo
- **URL:** http://localhost:8004
- **Puerto:** 8004
- **Estado:** ✅ Healthy

### 🧪 Pruebas con PowerShell

#### 6.1 Health Check
```powershell
Invoke-WebRequest -Uri http://localhost:8004/health -Method GET
```

#### 6.2 Enviar Email de Prueba
```powershell
$body = @{
    to_email = "tu_email@example.com"
    subject = "Prueba de Notificaciones"
    body = "Este es un email de prueba del sistema"
    template = "generic"
} | ConvertTo-Json

Invoke-WebRequest -Uri http://localhost:8004/send-email -Method POST -Body $body -ContentType "application/json"
```

**Verificar:**
- [ ] Status 200
- [ ] Email recibido en bandeja de entrada
- [ ] Formato correcto del email
- [ ] Logo y diseño corporativo

#### 6.3 Email de Bienvenida
```powershell
$body = @{
    to_email = "nuevo_usuario@example.com"
    username = "nuevo_usuario"
} | ConvertTo-Json

Invoke-WebRequest -Uri http://localhost:8004/send-welcome-email -Method POST -Body $body -ContentType "application/json"
```

**Verificar:**
- [ ] Status 200
- [ ] Email con template de bienvenida
- [ ] Información personalizada del usuario

#### 6.4 Email de Confirmación de Reserva
```powershell
$body = @{
    to_email = "usuario@example.com"
    reservation_details = @{
        reservation_id = 123
        license_type = "Conducir"
        reservation_date = "2025-11-15"
        reservation_time = "09:00"
    }
} | ConvertTo-Json -Depth 3

Invoke-WebRequest -Uri http://localhost:8004/send-reservation-email -Method POST -Body $body -ContentType "application/json"
```

**Verificar:**
- [ ] Status 200
- [ ] Email con detalles de la reserva
- [ ] Formato de fecha/hora legible
- [ ] Instrucciones claras

#### 6.5 Verificar Cola de Celery
```bash
# Ver tareas en cola
docker logs celery_worker --tail 50
```

**Verificar:**
- [ ] Celery worker procesando tareas
- [ ] Sin errores en los logs
- [ ] Tareas completadas exitosamente

---

## 7. CHATBOT IA (100% GRATUITO)

### 🌐 Acceso
- **ChatBot Service:** http://localhost:8005
- **Ollama Service:** http://localhost:11434
- **Modelo:** Llama 2 (Local, 100% Gratuito)
- **Estado:** ✅ Healthy

### 🧪 Pruebas con PowerShell

#### 7.1 Health Check - ChatBot Service
```powershell
Invoke-WebRequest -Uri http://localhost:8005/health -Method GET
```

#### 7.2 Health Check - Ollama Service
```powershell
Invoke-WebRequest -Uri http://localhost:11434/api/tags -Method GET
```

**Verificar:**
- [ ] Status 200
- [ ] Modelo "llama2:latest" listado
- [ ] Tamaño del modelo: ~3.8 GB

#### 7.3 Chat con el Bot (Requiere Autenticación)
```powershell
$body = @{
    message = "Hola, ¿cómo puedo hacer una reservación?"
    session_id = "test-session-123"
} | ConvertTo-Json

$headers = @{
    Authorization = "Bearer $token"
}

Invoke-WebRequest -Uri http://localhost:8005/chat -Method POST -Body $body -ContentType "application/json" -Headers $headers
```

**Verificar:**
- [ ] Status 200
- [ ] Respuesta coherente en español
- [ ] session_id devuelto
- [ ] Tiempo de respuesta razonable (5-15 segundos)

#### 7.4 Historial de Chat
```powershell
$sessionId = "test-session-123"

$headers = @{
    Authorization = "Bearer $token"
}

Invoke-WebRequest -Uri "http://localhost:8005/chat/history/$sessionId" -Method GET -Headers $headers
```

**Verificar:**
- [ ] Status 200
- [ ] Array de mensajes (usuario y bot)
- [ ] Orden cronológico correcto

#### 7.5 Limpiar Sesión
```powershell
$headers = @{
    Authorization = "Bearer $token"
}

Invoke-WebRequest -Uri "http://localhost:8005/chat/session/$sessionId" -Method DELETE -Headers $headers
```

**Verificar:**
- [ ] Status 200
- [ ] Sesión marcada como inactiva
- [ ] Historial limpiado

#### 7.6 Prueba Directa con Ollama
```powershell
$body = @{
    model = "llama2"
    prompt = "¿Qué es una licencia de conducir?"
    stream = $false
} | ConvertTo-Json

Invoke-WebRequest -Uri http://localhost:11434/api/generate -Method POST -Body $body -ContentType "application/json"
```

**Verificar:**
- [ ] Status 200
- [ ] Respuesta generada por Llama 2
- [ ] Sin errores de modelo

#### 7.7 Verificar Métricas del ChatBot
```powershell
$headers = @{
    Authorization = "Bearer $token"
}

Invoke-WebRequest -Uri http://localhost:8005/chat/metrics -Method GET -Headers $headers
```

**Verificar:**
- [ ] Total de conversaciones
- [ ] Total de mensajes
- [ ] Tiempo promedio de respuesta

---

## 8. BASES DE DATOS POSTGRESQL

### 🗄️ Configuración
- **Auth DB:** Puerto 5432 (Primary) + Replica
- **Reservations DB:** Puerto 5433 (Primary) + Replica
- **Documents DB:** Puerto 5434 (Primary) + Replica
- **ChatBot DB:** Puerto 5435 (Primary) + Replica

### 🧪 Pruebas con PowerShell

#### 8.1 Conexión a Auth Database
```powershell
# Requiere psql instalado
docker exec -it auth_db_primary psql -U admin -d auth_db -c "\dt"
```

**Verificar:**
- [ ] Conexión exitosa
- [ ] Tablas: users, sessions, etc.

#### 8.2 Verificar Replicación
```powershell
# En Primary
docker exec -it auth_db_primary psql -U admin -d auth_db -c "SELECT * FROM pg_stat_replication;"

# En Replica
docker exec -it auth_db_replica psql -U replicator -d auth_db -c "SELECT pg_is_in_recovery();"
```

**Verificar:**
- [ ] Primary muestra replica conectada
- [ ] Replica en modo recovery (true)
- [ ] Lag de replicación < 1 segundo

#### 8.3 Test de Escritura/Lectura
```powershell
# Escribir en Primary
docker exec -it auth_db_primary psql -U admin -d auth_db -c "INSERT INTO users (username, email) VALUES ('test', 'test@test.com');"

# Leer desde Replica (esperar 1-2 segundos)
Start-Sleep -Seconds 2
docker exec -it auth_db_replica psql -U admin -d auth_db -c "SELECT * FROM users WHERE username='test';"
```

**Verificar:**
- [ ] Dato insertado en Primary
- [ ] Dato replicado en Replica
- [ ] Tiempo de replicación < 2 segundos

#### 8.4 Verificar Bases de Datos del ChatBot
```powershell
docker exec -it chatbot_db_primary psql -U admin -d chatbot_db -c "\dt"
```

**Verificar:**
- [ ] Tablas: chat_sessions, chat_messages, chat_metrics
- [ ] Relaciones correctas entre tablas

---

## 9. ALMACENAMIENTO MINIO

### 🗄️ Acceso
- **API:** http://localhost:9000
- **Console:** http://localhost:9001
- **Usuario:** minioadmin
- **Contraseña:** minioadmin123

### 🧪 Pruebas en Navegador

#### 9.1 Acceso a Console
1. Abrir http://localhost:9001
2. Login con credenciales:
   - Usuario: `minioadmin`
   - Contraseña: `minioadmin123`

**Verificar:**
- [ ] Login exitoso
- [ ] Dashboard visible
- [ ] Buckets creados

#### 9.2 Verificar Buckets
**En MinIO Console:**
1. Click en "Buckets" en menú lateral
2. Verificar buckets existentes:
   - `documents` - Para archivos de usuarios
   - `db-backups` - Para backups de bases de datos

**Verificar:**
- [ ] Buckets visibles
- [ ] Permisos configurados
- [ ] Cuota de almacenamiento

#### 9.3 Subir Archivo Manual
1. Entrar a bucket "documents"
2. Click en "Upload"
3. Seleccionar archivo
4. Verificar upload exitoso

**Verificar:**
- [ ] Archivo subido correctamente
- [ ] Metadata visible
- [ ] Puede descargar el archivo

#### 9.4 Test con API (PowerShell)
```powershell
# Requiere AWS CLI o MinIO Client
# Instalar: choco install minio-client

mc alias set myminio http://localhost:9000 minioadmin minioadmin123
mc ls myminio
```

**Verificar:**
- [ ] Conexión exitosa
- [ ] Lista de buckets visible

---

## 10. SISTEMA DE MONITOREO

### 📊 Servicios de Monitoreo

#### 10.1 Prometheus
- **URL:** http://localhost:9090
- **Puerto:** 9090

**Pruebas:**
1. Abrir http://localhost:9090
2. Ir a Status > Targets
3. Verificar todos los targets están "UP"

**Verificar:**
- [ ] Prometheus UI carga
- [ ] Todos los exporters activos:
  - node-exporter (9100)
  - redis-exporter (9121)
  - postgres-exporter-auth (9187)
  - postgres-exporter-reservations (9188)
  - postgres-exporter-documents (9189)
  - postgres-exporter-chatbot (9190)

#### 10.2 Grafana
- **URL:** http://localhost:3001
- **Puerto:** 3001
- **Usuario:** admin
- **Contraseña:** change_me_grafana_secure

**Pruebas:**
1. Abrir http://localhost:3001
2. Login con credenciales
3. Verificar dashboards disponibles

**Verificar:**
- [ ] Login exitoso
- [ ] Dashboards predefinidos:
  - System Overview
  - Database Performance
  - API Response Times
- [ ] Gráficas muestran datos reales
- [ ] Alertas configuradas

#### 10.3 Alertmanager
- **URL:** http://localhost:9093
- **Puerto:** 9093

**Verificar:**
- [ ] UI de Alertmanager accesible
- [ ] Reglas de alerta configuradas
- [ ] Sin alertas activas (sistema saludable)

#### 10.4 Métricas de Servicios

**Node Exporter (Métricas del Sistema):**
```powershell
Invoke-WebRequest -Uri http://localhost:9100/metrics -Method GET
```
**Verificar:**
- [ ] CPU usage
- [ ] Memory usage
- [ ] Disk I/O

**Redis Exporter:**
```powershell
Invoke-WebRequest -Uri http://localhost:9121/metrics -Method GET
```
**Verificar:**
- [ ] Redis connected_clients
- [ ] Redis used_memory
- [ ] Redis commands_processed

**PostgreSQL Exporters:**
```powershell
# Auth DB
Invoke-WebRequest -Uri http://localhost:9187/metrics -Method GET

# Reservations DB
Invoke-WebRequest -Uri http://localhost:9188/metrics -Method GET

# Documents DB
Invoke-WebRequest -Uri http://localhost:9189/metrics -Method GET

# ChatBot DB
Invoke-WebRequest -Uri http://localhost:9190/metrics -Method GET
```
**Verificar:**
- [ ] pg_up = 1 (base de datos up)
- [ ] Conexiones activas
- [ ] Queries ejecutados

---

## 11. REDIS CACHE

### 🗄️ Acceso
- **URL:** localhost:6379
- **Puerto:** 6379
- **Estado:** ✅ Healthy

### 🧪 Pruebas con PowerShell

#### 11.1 Conectar a Redis
```powershell
docker exec -it redis_queue redis-cli
```

#### 11.2 Comandos de Prueba
```bash
# Dentro de redis-cli:
PING                    # Debe responder PONG
INFO                    # Información del servidor
DBSIZE                  # Número de keys
KEYS *                  # Listar todas las keys (cuidado en producción)

# Test de escritura/lectura
SET test_key "test_value"
GET test_key
DEL test_key

# Verificar keys de sesiones
KEYS session:*

# Ver estadísticas
INFO stats
```

**Verificar:**
- [ ] PING responde PONG
- [ ] Redis version >= 7
- [ ] Keys de sesiones presentes
- [ ] used_memory razonable

#### 11.3 Monitorear Actividad en Tiempo Real
```powershell
docker exec -it redis_queue redis-cli MONITOR
```
Luego hacer login en el frontend y ver comandos de Redis en tiempo real.

**Verificar:**
- [ ] Comandos SET/GET cuando usuario hace login
- [ ] Keys con prefijo correcto
- [ ] TTL configurado en sesiones

---

## 12. BACKUPS AUTOMÁTICOS

### 💾 Configuración
- **Servicio:** pg_backup
- **Horario:** 03:00 AM diario (configurable en .env)
- **Retención:** 7 días
- **Destino:** MinIO bucket "db-backups"

### 🧪 Pruebas

#### 12.1 Ejecutar Backup Manual
```powershell
docker exec -it pg_backup /app/backup.sh
```

**Verificar:**
- [ ] Comando ejecuta sin errores
- [ ] Mensaje de confirmación
- [ ] Tiempo de ejecución razonable

#### 12.2 Verificar Archivos de Backup
```powershell
# En MinIO Console
# 1. Ir a http://localhost:9001
# 2. Entrar a bucket "db-backups"
# 3. Verificar archivos .sql.gz

# O con comando:
docker exec -it pg_backup ls -lh /backups
```

**Verificar:**
- [ ] Archivos .sql.gz creados
- [ ] Nombres con timestamp
- [ ] Tamaño > 0 (no vacíos)
- [ ] Backup de todas las DBs:
  - auth_db_*.sql.gz
  - reservations_db_*.sql.gz
  - documents_db_*.sql.gz
  - chatbot_db_*.sql.gz

#### 12.3 Test de Restauración
```powershell
# Ver backups disponibles
docker exec -it pg_backup ls /backups

# Restaurar un backup (¡CUIDADO! Esto sobrescribe datos)
docker exec -it pg_backup /app/restore-db.sh auth_db auth_db_20251109_030000.sql.gz
```

**Verificar:**
- [ ] Restauración exitosa
- [ ] Datos recuperados
- [ ] Integridad de datos

#### 12.4 Verificar Logs de Backup
```powershell
docker logs pg_backup --tail 100
```

**Verificar:**
- [ ] Logs de ejecuciones pasadas
- [ ] Sin errores críticos
- [ ] Confirmación de uploads a MinIO

---

## 📋 CHECKLIST COMPLETO DE VERIFICACIÓN

### ✅ Servicios Core
- [ ] Frontend carga y funciona
- [ ] API Gateway enruta correctamente
- [ ] Auth Service autentica usuarios
- [ ] Reservations Service gestiona reservas
- [ ] Documents Service maneja archivos
- [ ] Notifications Service envía emails
- [ ] ChatBot IA responde preguntas (100% gratuito)

### ✅ Bases de Datos
- [ ] Auth DB: Primary + Replica funcionando
- [ ] Reservations DB: Primary + Replica funcionando
- [ ] Documents DB: Primary + Replica funcionando
- [ ] ChatBot DB: Primary + Replica funcionando
- [ ] Replicación activa en todas

### ✅ Infraestructura
- [ ] Redis caché funcionando
- [ ] MinIO almacenando archivos
- [ ] Ollama ejecutando modelo Llama 2
- [ ] Backups automáticos configurados

### ✅ Monitoreo
- [ ] Prometheus recolectando métricas
- [ ] Grafana mostrando dashboards
- [ ] Alertmanager configurado
- [ ] Todos los exporters activos

### ✅ Funcionalidades de Usuario
- [ ] Registro de usuario
- [ ] Login exitoso
- [ ] Crear reservación
- [ ] Ver mis reservas
- [ ] Cancelar reserva
- [ ] Subir documento
- [ ] Descargar documento
- [ ] Chat con bot IA
- [ ] Recibir notificaciones por email

### ✅ Seguridad
- [ ] Autenticación JWT funcionando
- [ ] Contraseñas hasheadas
- [ ] CORS configurado
- [ ] Headers de seguridad
- [ ] Validación de inputs

### ✅ Alta Disponibilidad
- [ ] Múltiples instancias de servicios
- [ ] Balanceo de carga
- [ ] Replicación de bases de datos
- [ ] Backups automáticos
- [ ] Health checks activos

---

## 🚀 COMANDOS ÚTILES

### Ver Estado General
```powershell
docker compose ps
```

### Ver Logs de un Servicio
```powershell
docker logs <nombre_contenedor> --tail 100 -f
```

### Reiniciar un Servicio
```powershell
docker compose restart <nombre_servicio>
```

### Ver Uso de Recursos
```powershell
docker stats
```

### Verificar Red
```powershell
docker network inspect proyecto_default
```

---

## 📞 SOLUCIÓN DE PROBLEMAS

### Servicio No Responde
1. Verificar que está corriendo: `docker compose ps`
2. Ver logs: `docker logs <contenedor>`
3. Reiniciar: `docker compose restart <servicio>`

### Base de Datos No Conecta
1. Verificar puerto: `docker compose ps | Select-String postgres`
2. Test de conexión: `docker exec -it <db_container> psql -U admin -d <db_name>`
3. Ver logs de replica: `docker logs <db_replica>`

### Email No Llega
1. Verificar logs: `docker logs notifications_service`
2. Verificar logs de Celery: `docker logs celery_worker`
3. Revisar configuración SMTP en .env

### ChatBot No Responde
1. Verificar Ollama: `curl http://localhost:11434/api/tags`
2. Ver logs ChatBot: `docker logs chatbot_service_1`
3. Ver logs Ollama: `docker logs ollama_service`

---

## 🎯 CRITERIOS DE ÉXITO

El sistema se considera **COMPLETAMENTE FUNCIONAL** si:

1. ✅ Todos los servicios están en estado "Healthy"
2. ✅ Usuario puede registrarse y hacer login
3. ✅ Usuario puede crear y ver reservaciones
4. ✅ Usuario puede subir y descargar documentos
5. ✅ Usuario recibe emails de confirmación
6. ✅ ChatBot responde preguntas coherentemente
7. ✅ Todas las bases de datos están replicadas
8. ✅ Backups se ejecutan automáticamente
9. ✅ Monitoreo muestra métricas en tiempo real
10. ✅ No hay errores críticos en los logs

---

## 📝 NOTAS FINALES

- **Modelo de IA:** Llama 2 corriendo localmente en Ollama (100% GRATUITO)
- **Escalabilidad:** Servicios con múltiples instancias y balanceo de carga
- **Resiliencia:** Replicación de bases de datos y backups automáticos
- **Observabilidad:** Stack completo de monitoreo (Prometheus + Grafana)
- **Seguridad:** Autenticación JWT, validación de inputs, CORS configurado

---

**✅ SISTEMA LISTO PARA PRODUCCIÓN**
