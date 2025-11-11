# Sistema Municipal de Gestión Digital
## Proyecto de Administración de Redes - Universidad de Talca

---

## 📋 Descripción General

Sistema integral de gestión municipal basado en arquitectura de microservicios que proporciona:
- **Reservas de citas** para trámites municipales con validación de requisitos
- **Digitalización de documentos** ciudadanos y archivo histórico
- **Gestión de datos municipales** (licencias, permisos, patentes, multas)
- **Chatbot con IA local** (Ollama/llama3.2) para asistencia ciudadana 24/7
- **Panel administrativo** completo con reportes y analíticas
- **Alta disponibilidad** con replicación de bases de datos y balanceo de carga
- **Monitoreo completo** con Prometheus, Grafana y Alertmanager

---

## 🏗️ Arquitectura Técnica

### Stack Tecnológico
```yaml
Frontend:
  - React 18 + Vite
  - Tailwind CSS
  - Axios
  - nginx (servidor web)

Backend:
  - Python 3.11
  - FastAPI (microservicios)
  - SQLModel + PostgreSQL 16.4
  - Celery + Redis (colas asíncronas)

IA y NLP:
  - Ollama (servidor LLM local)
  - llama3.2:1b (modelo de lenguaje)

Infraestructura:
  - Docker + Docker Compose
  - nginx (API Gateway + Load Balancer)
  - PostgreSQL con streaming replication
  - MinIO (almacenamiento S3-compatible)
  - Redis (cache y colas)

Monitoreo:
  - Prometheus (métricas)
  - Grafana (visualización)
  - Alertmanager (alertas)
  - Node Exporter + PostgreSQL Exporter
```

### Servicios y Puertos
```
┌─────────────────────────────────────────────────────────────┐
│                      ACCESO PÚBLICO                          │
├─────────────────────────────────────────────────────────────┤
│ Frontend:           http://localhost:3000                    │
│ API Gateway:        http://localhost:8081                    │
│ Grafana:            http://localhost:3001                    │
│ Prometheus:         http://localhost:9090                    │
│ Alertmanager:       http://localhost:9093                    │
│ MinIO Console:      http://localhost:9001                    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                   MICROSERVICIOS (Internos)                  │
├─────────────────────────────────────────────────────────────┤
│ auth-service-1/2:           8000 (HA - 2 instancias)        │
│ reservations-service-1/2:   8002 (HA - 2 instancias)        │
│ documents-service:          8003                             │
│ notifications-service:      8004                             │
│ chatbot-service:            8005                             │
│ datos-municipalidad:        8006                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                  BASES DE DATOS (Expuestas)                  │
├─────────────────────────────────────────────────────────────┤
│ auth-db (primary):          5432 + replica                  │
│ reservations-db (primary):  5433 + replica                  │
│ documents-db:               5434                             │
│ chatbot-db:                 5436                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Arranque Rápido

### Pre-requisitos
```bash
# Requerido
- Docker 24.0+
- Docker Compose 2.20+
- 8GB RAM mínimo
- 20GB espacio en disco

# Opcional (para desarrollo)
- Python 3.11+
- Node.js 20+
```

### Instalación

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd proyecto
```

2. **Configurar variables de entorno**
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

3. **Iniciar todos los servicios**
```powershell
# Windows PowerShell
docker compose up -d --build

# Linux/Mac
docker-compose up -d --build
```

4. **Verificar el estado**
```powershell
docker compose ps
```

5. **Acceder al sistema**
- Frontend: http://localhost:3000
- API Gateway: http://localhost:8081
- Grafana: http://localhost:3001 (admin/admin123)
- Prometheus: http://localhost:9090

### Usuarios de Prueba
```yaml
Administrador:
  Email: admin@municipalidad.cl
  RUT: 11111111-1
  Password: admin123
  Rol: admin

Empleado:
  Email: empleado@municipalidad.cl
  RUT: 22222222-2
  Password: empleado123
  Rol: employee

Ciudadano:
  Email: ciudadano@example.cl
  RUT: 33333333-3
  Password: ciudadano123
  Rol: user
```

---

## 🔧 Microservicios

### 1. Auth Service
**Responsabilidades:** Autenticación, autorización, gestión de usuarios
- JWT con RS256
- RBAC (Role-Based Access Control)
- Simulador de datos municipales
- 2 instancias para alta disponibilidad

**Endpoints principales:**
- `POST /token` - Login
- `GET /users/me` - Usuario actual
- `POST /admin/employees` - Registrar empleados
- `GET /consultar-datos-municipales` - Datos municipales

### 2. Documents Service
**Responsabilidades:** Gestión y digitalización de documentos
- Upload de documentos ciudadanos
- Digitalización de archivos antiguos
- Validación y procesamiento de archivos
- Reportes de digitalización
- Almacenamiento en MinIO

**Endpoints principales:**
- `POST /upload-documento` - Subir documento
- `GET /documentos/usuario/{id}` - Documentos de usuario
- `POST /documentos-antiguos` - Digitalizar antiguo
- `GET /reportes/digitalizacion/diario` - Reportes

### 3. Reservations Service
**Responsabilidades:** Sistema de reservas de citas
- Gestión de reservas
- Validación de disponibilidad horaria
- Requisitos por tipo de trámite
- Notificaciones automáticas
- 2 instancias para alta disponibilidad

**Endpoints principales:**
- `POST /reservations` - Crear reserva
- `GET /reservations/user/{id}` - Reservas de usuario
- `GET /check-availability` - Verificar disponibilidad
- `POST /validar-requisitos-tramite` - Validar requisitos

### 4. AI Service (Chatbot)
**Responsabilidades:** Asistencia con IA
- Procesamiento de lenguaje natural con Ollama
- Base de conocimiento municipal
- Historial de conversaciones
- Modelo llama3.2:1b (100% gratuito)

**Endpoints principales:**
- `POST /chat/public` - Chat público
- `POST /chat` - Chat autenticado
- `GET /sessions/{user_id}` - Historial
- `DELETE /sessions/{session_id}` - Limpiar sesión

### 5. Notifications Service
**Responsabilidades:** Envío de notificaciones
- Emails transaccionales
- Cola asíncrona con Celery + Redis
- Templates HTML
- Reintento automático

**Endpoints principales:**
- `POST /send-email` - Enviar email
- `POST /send-welcome-email` - Email de bienvenida
- `POST /send-reservation-confirmation` - Confirmar reserva

### 6. Datos Municipalidad Service
**Responsabilidades:** Simulador de sistemas municipales
- Consultas a sistemas legacy
- Licencias de conducir
- Permisos de edificación
- Patentes comerciales
- Multas JPL

---

## 🗄️ Base de Datos

### Arquitectura de Replicación
```
Auth DB:           Primary (5432) ──► Replica (streaming)
Reservations DB:   Primary (5433) ──► Replica (streaming)
Documents DB:      Primary (5434) - Sin réplica
Chatbot DB:        Primary (5436) - Sin réplica
```

### Características
- PostgreSQL 16.4
- Streaming replication para HA
- Backups automáticos diarios (pg-backup)
- Monitoring con postgres_exporter
- Connection pooling

### Esquemas Principales

**Auth Database:**
- `users` - Usuarios del sistema
- `datos_municipales` - Cache de consultas

**Documents Database:**
- `documentos_ciudadano` - Docs asociados a reservas
- `documentos_antiguos` - Archivo histórico digitalizado
- `registro_digitalizacion` - Auditoría

**Reservations Database:**
- `reservations` - Reservas de citas
- `requisitos_tramites` - Requisitos por trámite
- `disponibilidad_horaria` - Calendario

---

## 📊 Monitoreo y Observabilidad

### Prometheus
- **URL:** http://localhost:9090
- Métricas de todos los servicios
- Alertas configuradas
- Retention: 15 días

### Grafana
- **URL:** http://localhost:3001
- Usuario: admin / admin123
- Dashboards pre-configurados:
  - Sistema (CPU, memoria, disco)
  - Bases de datos (conexiones, queries)
  - Aplicación (requests, latencia)

### Métricas Clave
```yaml
Disponibilidad:
  - Uptime de servicios
  - Health checks
  - Database replication lag

Performance:
  - Response time por endpoint
  - Throughput (requests/s)
  - Error rate

Recursos:
  - CPU usage por servicio
  - Memory usage
  - Disk I/O
  - Network traffic
```

### Alertas Configuradas
```yaml
Critical:
  - Service down > 1 min
  - DB connection failure
  - Error rate > 5%
  - CPU > 80%
  - Memory > 90%

Warning:
  - Response time > 2s
  - Replication lag > 30s
  - Disk space < 20%
```

---

## 🔐 Seguridad

### Autenticación
- JWT (JSON Web Tokens) con algoritmo RS256
- Tokens válidos por 24 horas
- Headers: `Authorization: Bearer <token>`

### Autorización (RBAC)
```yaml
Roles:
  user:     # Ciudadanos
    - Ver sus reservas
    - Crear reservas
    - Subir documentos
    - Usar chatbot

  employee: # Empleados municipales
    - Todo lo de user +
    - Revisar documentos
    - Digitalizar archivos
    - Ver reportes básicos

  admin:    # Administradores
    - Todo lo anterior +
    - Gestión de usuarios
    - Reportes completos
    - Configuración sistema
```

### Headers de Seguridad (nginx)
```nginx
X-Frame-Options: SAMEORIGIN
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Content-Security-Policy: default-src 'self'
```

---

## 🌐 Alta Disponibilidad (HA)

### Balanceo de Carga
El API Gateway (nginx) distribuye las peticiones:
```nginx
Auth Service:         Round-robin entre 2 instancias
Reservations Service: Round-robin entre 2 instancias
Otros servicios:      Instancia única
```

### Replicación de Bases de Datos
- **Streaming replication** PostgreSQL
- Réplica asíncrona para alta disponibilidad
- Failover manual configurado

### Pruebas de HA

**Probar Alta Disponibilidad de Servicios:**
```powershell
# 1. Verificar estado
docker compose ps

# 2. Probar servicio
curl http://localhost:8081/api/auth/health

# 3. Detener una réplica
docker compose stop auth-service-1

# 4. El servicio sigue respondiendo (auth-service-2)
curl http://localhost:8081/api/auth/health

# 5. Recuperar réplica
docker compose start auth-service-1
```

**Probar Replicación de BD:**
```powershell
# Ver estado de replicación
docker compose exec auth-db psql -U auth_user -d auth_db -c "SELECT client_addr, state, sync_state FROM pg_stat_replication;"

# Confirmar que réplica está en standby
docker compose exec auth-db-replica psql -U auth_user -d auth_db -c "SELECT pg_is_in_recovery();"
```

Ver documento completo: `docs/pruebas-ha-replicacion.md`

---

## 📦 Backups

### Automáticos
- Servicio `pg-backup` ejecuta backups diarios
- Cron schedule: `0 3 * * *` (3 AM)
- Retention: 7 días
- Upload a MinIO

### Manual
```powershell
# Ejecutar backup inmediato
docker compose run --rm -e BACKUP_ONCE=1 pg-backup /bin/sh -c "/app/backup.sh && ls -l /backups"
```

### Restauración
```bash
# Restaurar desde backup
docker compose exec pg-backup /app/restore-db.sh <db_host> <db_name> <db_user> <db_password> [archivo.sql]
```

---

## 🧪 Testing

### Health Checks
```powershell
# Todos los servicios tienen endpoint /health
curl http://localhost:8081/api/auth/health
curl http://localhost:8081/api/reservations/health
curl http://localhost:8081/api/documents/health
curl http://localhost:8081/api/notifications/health
curl http://localhost:8081/api/chatbot/health
```

### Scripts de Prueba
```powershell
# Prueba rápida del sistema
.\test_quick.ps1

# Prueba completa de servicios
.\test_all_services.ps1

# Prueba del chatbot IA
.\test_chatbot_final.ps1

# Prueba de HA y replicación
# Ver: docs/pruebas-ha-replicacion.md
```

---

## 📚 Documentación Adicional

```
docs/
├── arquitectura.md              # Arquitectura detallada
├── pruebas-ha-replicacion.md   # Pruebas de HA paso a paso
├── chatbot-service.md          # Documentación del chatbot
├── plan-reportes.md            # Sistema de reportes
├── monitoring_README.md        # Guía de monitoreo
└── validacion-horarios.md      # Validación de reservas
```

### Documentos de Guías
- `GUIA_API_RESERVACIONES.md` - API de reservas
- `GUIA_FRONTEND_RESERVACIONES.md` - Frontend
- `GUIA_CHATBOT_QUICKSTART.md` - Chatbot quickstart
- `GUIA_PRUEBAS_COMPLETA.md` - Testing completo
- `DEPLOYMENT_CHATBOT.md` - Deploy del chatbot
- `INTEGRACION_NOTIFICACIONES.md` - Sistema de notificaciones

### Informes Técnicos
- `RESUMEN_ARQUITECTURA_COMPLETA.md` - Arquitectura completa
- `RESUMEN_EJECUTIVO_FINAL.md` - Resumen ejecutivo
- `INFORME_VERIFICACION_SISTEMA.md` - Verificación del sistema
- `PROPUESTA_ECONOMICA_LICITACION.md` - Propuesta económica

---

## 🛠️ Desarrollo

### Estructura del Proyecto
```
proyecto/
├── services/                    # Microservicios
│   ├── auth-service/
│   ├── documents-service/
│   ├── reservations-service/
│   ├── notifications-service/
│   ├── ai-service/
│   ├── datos-municipalidad-service/
│   ├── frontend/
│   └── api-gateway/
├── infrastructure/              # Infraestructura
│   ├── database/               # Scripts SQL
│   ├── postgres/               # Init scripts
│   ├── monitoring/             # Prometheus/Grafana
│   └── pg-backup/              # Backups
├── docs/                       # Documentación
├── docker-compose.yml          # Orquestación
└── .env                        # Variables de entorno
```

### Comandos Útiles
```powershell
# Ver logs de un servicio
docker compose logs -f auth-service-1

# Rebuild un servicio específico
docker compose up -d --build auth-service-1

# Escalar servicios
docker compose up -d --scale auth-service=3

# Detener todo
docker compose down

# Limpiar volúmenes (⚠️ borra datos)
docker compose down -v
```

---

## 🚦 Estado del Proyecto

### Completado ✅
- [x] Arquitectura de microservicios
- [x] Sistema de autenticación JWT + RBAC
- [x] Servicio de reservas con validación
- [x] Digitalización de documentos
- [x] Chatbot con IA local (Ollama)
- [x] Sistema de notificaciones
- [x] Alta disponibilidad (HA)
- [x] Replicación de bases de datos
- [x] API Gateway con load balancing
- [x] Monitoreo completo (Prometheus + Grafana)
- [x] Backups automáticos
- [x] Frontend React responsive
- [x] Documentación completa

### En Progreso 🔄
- [ ] Tests automatizados unitarios
- [ ] CI/CD pipeline
- [ ] Cache con Redis
- [ ] Rate limiting

### Planificado 📋
- [ ] Mobile app (React Native)
- [ ] SSO con sistemas externos
- [ ] ML para categorización de docs
- [ ] Blockchain para trazabilidad

---

## 🤝 Contribución

Este es un proyecto académico de la Universidad de Talca para la asignatura de Administración de Redes.

**Equipo:**
- Curso: Administración de Redes
- Semestre: 2025-II
- Universidad: Universidad de Talca

---

## 📄 Licencia

Proyecto académico - Universidad de Talca © 2025

---

## 📞 Soporte

Para preguntas técnicas o issues:
- Ver documentación en `/docs`
- Revisar logs: `docker compose logs <servicio>`
- Health checks: `http://localhost:8081/api/<servicio>/health`

---

**Última actualización:** Noviembre 2025  
**Versión:** 1.0.0
