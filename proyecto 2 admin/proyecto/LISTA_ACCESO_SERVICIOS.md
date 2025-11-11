# 🌐 LISTA RÁPIDA DE ACCESO - TODOS LOS SERVICIOS

## 📱 INTERFACES DE USUARIO (Navegador Web)

### 1. **Frontend Principal - Aplicación Web**
```
URL: http://localhost:3000
Puerto: 3000
Descripción: Interfaz principal del sistema
Acceso: Público (requiere registro/login)
```
**Funcionalidades:**
- Registro e inicio de sesión
- Dashboard de usuario
- Gestión de reservaciones
- Subida/descarga de documentos
- ChatBot de ayuda integrado

---

### 2. **API Gateway - Punto de Entrada**
```
URL: http://localhost
Puerto: 80
Descripción: Entrada unificada a todas las APIs
```
**Endpoints disponibles:**
- `/api/auth/*` → Servicio de Autenticación
- `/api/reservations/*` → Servicio de Reservaciones
- `/api/documents/*` → Servicio de Documentos
- `/api/notifications/*` → Servicio de Notificaciones
- `/api/chatbot/*` → Servicio de ChatBot IA

---

### 3. **MinIO Console - Almacenamiento de Archivos**
```
URL: http://localhost:9001
Puerto: 9001
Usuario: minioadmin
Contraseña: minioadmin123
Descripción: Panel de administración de archivos
```
**Funcionalidades:**
- Explorar buckets (documents, db-backups)
- Subir/descargar archivos manualmente
- Gestión de permisos
- Monitoreo de almacenamiento

---

### 4. **Grafana - Dashboard de Monitoreo**
```
URL: http://localhost:3001
Puerto: 3001
Usuario: admin
Contraseña: change_me_grafana_secure
Descripción: Visualización de métricas y alertas
```
**Dashboards disponibles:**
- System Overview
- Database Performance
- API Response Times
- Container Health

---

### 5. **Prometheus - Métricas del Sistema**
```
URL: http://localhost:9090
Puerto: 9090
Descripción: Base de datos de métricas
Acceso: Público
```
**Secciones útiles:**
- Status → Targets (ver servicios monitoreados)
- Graph (consultar métricas)
- Alerts (ver reglas de alerta)

---

### 6. **Alertmanager - Gestión de Alertas**
```
URL: http://localhost:9093
Puerto: 9093
Descripción: Administrador de alertas
Acceso: Público
```

---

## 🔌 APIs DE SERVICIOS (Acceso Directo)

### 7. **Auth Service - Autenticación**
```
URL Base: http://localhost:8000
Puerto: 8000
Documentación: http://localhost:8000/docs
```
**Endpoints principales:**
- `POST /register` - Registrar usuario
- `POST /login` - Iniciar sesión
- `GET /me` - Obtener perfil
- `POST /change-password` - Cambiar contraseña
- `GET /health` - Estado del servicio

---

### 8. **Reservations Service - Gestión de Reservas**
```
URL Base: http://localhost:8002
Puerto: 8002
Documentación: http://localhost:8002/docs
```
**Endpoints principales:**
- `GET /availability` - Ver disponibilidad
- `POST /reservations` - Crear reserva
- `GET /reservations/my` - Mis reservas
- `GET /reservations/{id}` - Detalle de reserva
- `PATCH /reservations/{id}/status` - Actualizar estado
- `POST /reservations/{id}/cancel` - Cancelar reserva
- `GET /health` - Estado del servicio

---

### 9. **Documents Service - Gestión de Documentos**
```
URL Base: http://localhost:8003
Puerto: 8003
Documentación: http://localhost:8003/docs
```
**Endpoints principales:**
- `POST /documents/upload` - Subir documento
- `GET /documents/my` - Mis documentos
- `GET /documents/{id}` - Detalle de documento
- `GET /documents/{id}/download` - Descargar documento
- `DELETE /documents/{id}` - Eliminar documento
- `GET /health` - Estado del servicio

---

### 10. **Notifications Service - Envío de Emails**
```
URL Base: http://localhost:8004
Puerto: 8004
Documentación: http://localhost:8004/docs
```
**Endpoints principales:**
- `POST /send-email` - Enviar email genérico
- `POST /send-welcome-email` - Email de bienvenida
- `POST /send-reservation-email` - Email de confirmación
- `GET /health` - Estado del servicio

---

### 11. **ChatBot Service - Asistente Virtual IA**
```
URL Base: http://localhost:8005
Puerto: 8005
Documentación: http://localhost:8005/docs
```
**Endpoints principales:**
- `POST /chat` - Enviar mensaje al bot
- `GET /chat/history/{session_id}` - Historial de chat
- `DELETE /chat/session/{session_id}` - Limpiar sesión
- `GET /chat/metrics` - Métricas de uso
- `GET /chat/sessions` - Sesiones activas
- `GET /health` - Estado del servicio

**⭐ NOTA:** Este servicio usa **Ollama + Llama 2** (100% GRATUITO)

---

### 12. **Ollama Service - Motor de IA Local**
```
URL Base: http://localhost:11434
Puerto: 11434
```
**Endpoints:**
- `GET /api/tags` - Listar modelos instalados
- `POST /api/generate` - Generar respuesta
- `POST /api/pull` - Descargar modelo

---

## 📊 EXPORTERS DE MÉTRICAS

### 13. **Node Exporter - Métricas del Sistema**
```
URL: http://localhost:9100/metrics
Puerto: 9100
```
**Métricas disponibles:**
- CPU usage
- Memory usage
- Disk I/O
- Network traffic

---

### 14. **Redis Exporter - Métricas de Cache**
```
URL: http://localhost:9121/metrics
Puerto: 9121
```

---

### 15-18. **PostgreSQL Exporters - Métricas de Bases de Datos**

**Auth Database:**
```
URL: http://localhost:9187/metrics
Puerto: 9187
```

**Reservations Database:**
```
URL: http://localhost:9188/metrics
Puerto: 9188
```

**Documents Database:**
```
URL: http://localhost:9189/metrics
Puerto: 9189
```

**ChatBot Database:**
```
URL: http://localhost:9190/metrics
Puerto: 9190
```

---

## 🗄️ BASES DE DATOS (Conexión Directa)

### 19. **Auth Database**
```
Host: localhost
Puerto: 5432
Usuario: admin
Contraseña: admin
Base de Datos: auth_db
```
**Conexión:**
```bash
docker exec -it auth_db_primary psql -U admin -d auth_db
```

---

### 20. **Reservations Database**
```
Host: localhost
Puerto: 5433
Usuario: admin
Contraseña: admin
Base de Datos: reservations_db
```
**Conexión:**
```bash
docker exec -it reservations_db_primary psql -U admin -d reservations_db
```

---

### 21. **Documents Database**
```
Host: localhost
Puerto: 5434
Usuario: admin
Contraseña: admin
Base de Datos: documents_db
```
**Conexión:**
```bash
docker exec -it documents_db_primary psql -U admin -d documents_db
```

---

### 22. **ChatBot Database**
```
Host: localhost
Puerto: 5435
Usuario: admin
Contraseña: admin
Base de Datos: chatbot_db
```
**Conexión:**
```bash
docker exec -it chatbot_db_primary psql -U admin -d chatbot_db
```

---

## 💾 ALMACENAMIENTO

### 23. **MinIO Storage (API)**
```
URL: http://localhost:9000
Puerto: 9000
Access Key: minioadmin
Secret Key: minioadmin123
```

---

### 24. **Redis Cache**
```
Host: localhost
Puerto: 6379
```
**Conexión:**
```bash
docker exec -it redis_queue redis-cli
```
**Comandos útiles:**
```
PING                 # Test conexión
INFO                 # Info del servidor
KEYS session:*       # Ver sesiones activas
DBSIZE              # Número de keys
```

---

## 🔍 COMANDOS RÁPIDOS DE VERIFICACIÓN

### Ver estado de todos los servicios:
```powershell
docker compose ps
```

### Ejecutar pruebas automatizadas:
```powershell
.\test_all_services.ps1
```

### Ver logs de un servicio:
```powershell
docker logs <nombre_contenedor> --tail 100 -f
```

### Reiniciar un servicio:
```powershell
docker compose restart <nombre_servicio>
```

### Ver uso de recursos:
```powershell
docker stats
```

---

## 📋 CHECKLIST DE ACCESO RÁPIDO

### ✅ Para Usuario Final:
- [ ] **Frontend:** http://localhost:3000
- [ ] **ChatBot:** Botón flotante en esquina inferior derecha del frontend
- [ ] **Recibir emails:** Verificar bandeja de entrada

### ✅ Para Desarrollador:
- [ ] **Documentación de APIs:**
  - Auth: http://localhost:8000/docs
  - Reservations: http://localhost:8002/docs
  - Documents: http://localhost:8003/docs
  - Notifications: http://localhost:8004/docs
  - ChatBot: http://localhost:8005/docs

### ✅ Para Administrador:
- [ ] **Grafana (Monitoreo):** http://localhost:3001
- [ ] **Prometheus (Métricas):** http://localhost:9090
- [ ] **MinIO (Archivos):** http://localhost:9001
- [ ] **Bases de Datos:** Puertos 5432-5435
- [ ] **Logs:** `docker logs <contenedor>`

### ✅ Para DevOps:
- [ ] **Alertmanager:** http://localhost:9093
- [ ] **Exporters:** Puertos 9100, 9121, 9187-9190
- [ ] **Backups:** `docker exec pg_backup ls /backups`
- [ ] **Redis CLI:** `docker exec -it redis_queue redis-cli`

---

## 🚀 FLUJO DE PRUEBA COMPLETO (5 MINUTOS)

### 1. Verificar servicios (30 segundos)
```powershell
.\test_all_services.ps1
```

### 2. Probar Frontend (2 minutos)
1. Abrir http://localhost:3000
2. Registrar usuario
3. Iniciar sesión
4. Crear una reservación
5. Probar ChatBot

### 3. Verificar Email (30 segundos)
- Revisar email de bienvenida
- Revisar email de confirmación de reserva

### 4. Verificar Monitoreo (1 minuto)
1. Abrir http://localhost:3001 (Grafana)
2. Ver dashboard "System Overview"
3. Verificar métricas en tiempo real

### 5. Verificar Almacenamiento (1 minuto)
1. Abrir http://localhost:9001 (MinIO)
2. Explorar bucket "documents"
3. Ver archivos subidos

---

## 📞 CONTACTO Y SOPORTE

**Para problemas técnicos:**
1. Revisar logs: `docker logs <servicio>`
2. Ver estado: `docker compose ps`
3. Consultar guía completa: `GUIA_PRUEBAS_COMPLETA.md`

**Archivos de configuración:**
- `.env` - Variables de entorno
- `docker-compose.yml` - Orquestación de servicios
- `GUIA_PRUEBAS_COMPLETA.md` - Guía detallada de pruebas

---

## ✅ SISTEMA 100% FUNCIONAL

**Servicios Core:** 7/7 ✅  
**Bases de Datos:** 4/4 ✅  
**Monitoreo:** 3/3 ✅  
**Almacenamiento:** 2/2 ✅  
**IA Gratuita:** 1/1 ✅ (Ollama + Llama 2)

**Total: 17/17 servicios operativos**

---

**Última actualización:** 9 de Noviembre de 2025  
**Versión del Sistema:** 1.0.0  
**Estado:** ✅ PRODUCCIÓN
