# 🤖 Documentación Técnica - Servicio ChatBot IA

## Índice
1. [Visión General](#visión-general)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Componentes Principales](#componentes-principales)
4. [API Endpoints](#api-endpoints)
5. [Base de Datos](#base-de-datos)
6. [Integración Frontend](#integración-frontend)
7. [Knowledge Base](#knowledge-base)
8. [Monitoreo y Métricas](#monitoreo-y-métricas)
9. [Deployment](#deployment)
10. [Mantenimiento](#mantenimiento)
11. [Troubleshooting](#troubleshooting)

---

## Visión General

### Propósito
El servicio de ChatBot IA es un microservicio independiente diseñado para proporcionar soporte automatizado e inteligente a los usuarios del sistema de reservas de licencias de conducir. Su objetivo principal es **reducir la carga de atención presencial y telefónica** respondiendo consultas frecuentes, guiando a los usuarios en la navegación del sistema, y proporcionando información detallada sobre trámites y requisitos.

### Características Clave
- ✅ **Asistente Conversacional Inteligente** - Powered by OpenAI GPT-3.5-turbo
- ✅ **Knowledge Base Contextual** - Información específica sobre licencias y trámites
- ✅ **Alta Disponibilidad** - 2 instancias con balanceo de carga
- ✅ **Persistencia de Sesiones** - Historial de conversaciones guardado
- ✅ **Detección de Contexto** - Respuestas adaptadas a la ubicación del usuario en el sistema
- ✅ **Métricas y Monitoreo** - Integración completa con Prometheus/Grafana
- ✅ **Interfaz Moderna** - Widget flotante en React con UX optimizada

### Tecnologías Utilizadas
- **Backend**: FastAPI 0.104.1 + Python 3.11
- **IA**: OpenAI GPT-3.5-turbo API
- **Base de Datos**: PostgreSQL 16.4 (con replicación)
- **Caché**: Redis 7
- **Contenedorización**: Docker + Docker Compose
- **Monitoreo**: Prometheus + Grafana
- **Frontend**: React + TailwindCSS

---

## Arquitectura del Sistema

### Diagrama de Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                     API Gateway (Nginx)                      │
│                   /api/chatbot/* → Round Robin              │
└────────────────┬─────────────────────┬──────────────────────┘
                 │                     │
        ┌────────▼─────────┐  ┌───────▼─────────┐
        │ chatbot-service-1│  │chatbot-service-2│
        │   Port: 8005     │  │   Port: 8005    │
        └────────┬─────────┘  └───────┬─────────┘
                 │                     │
                 └──────────┬──────────┘
                            │
            ┌───────────────┴───────────────┐
            │                               │
      ┌─────▼──────┐              ┌────────▼────────┐
      │ chatbot-db │──Replication─│chatbot-db-replica│
      │  (Primary) │◄─────────────│   (Standby)     │
      └────────────┘              └─────────────────┘
            │
      ┌─────▼──────┐
      │   Redis    │
      │  (Cache)   │
      └────────────┘
```

### Flujo de Datos

1. **Usuario** → Escribe mensaje en ChatBotWidget
2. **Frontend** → POST /api/chatbot/chat (con token JWT)
3. **API Gateway** → Balancea a chatbot-service-1 o chatbot-service-2
4. **ChatBot Service**:
   - Verifica JWT con auth-service
   - Obtiene/crea sesión en PostgreSQL
   - Recupera historial de conversación
   - Busca conocimiento relevante en knowledge_base.py
   - Construye contexto para OpenAI
   - Envía prompt a OpenAI GPT-3.5-turbo
   - Guarda respuesta en PostgreSQL
   - Actualiza métricas
5. **Backend** → Retorna respuesta al frontend
6. **Frontend** → Muestra mensaje del asistente

### Componentes de Infraestructura

| Componente | Instancias | Puerto | Propósito |
|------------|-----------|--------|-----------|
| chatbot-service | 2 | 8005 | Servicio principal FastAPI |
| chatbot-db | 1 primary + 1 replica | 5435 | Base de datos PostgreSQL |
| redis | 1 | 6379 | Caché y sesiones |
| API Gateway | 1 | 80 | Proxy reverso y balanceador |
| postgres-exporter-chatbot | 1 | 9190 | Métricas de PostgreSQL |

---

## Componentes Principales

### 1. main.py
**Archivo principal de la aplicación FastAPI**

- Define todos los endpoints HTTP
- Gestiona autenticación JWT
- Maneja ciclo de vida de la aplicación
- Configura CORS y middleware

**Endpoints principales:**
- `POST /chat` - Conversación con el bot
- `GET /chat/history/{session_id}` - Historial
- `DELETE /chat/session/{session_id}` - Limpiar sesión
- `GET /chat/metrics` - Métricas de usuario
- `GET /health` - Healthcheck

### 2. chatbot_service.py
**Lógica de negocio del chatbot**

```python
class ChatBotService:
    - create_session()           # Crear nueva sesión
    - get_or_create_session()    # Obtener o crear
    - generate_response()        # Generar respuesta con OpenAI
    - get_conversation_history() # Obtener historial
    - clear_session()            # Cerrar sesión
    - get_user_metrics()         # Obtener métricas
```

**Características:**
- Integración con OpenAI API
- Manejo de errores y rate limits
- Construcción de contexto conversacional
- Actualización de métricas automática
- Uso de Redis para caché

### 3. knowledge_base.py
**Base de conocimientos del sistema**

Contiene información estructurada sobre:

```python
KNOWLEDGE_BASE = {
    "sistema": {...},           # Info del sistema
    "licencias": {              # Tipos de licencias
        "clase_b": {...},
        "clase_a": {...},
        "renovacion": {...},
        "duplicado": {...}
    },
    "proceso_reserva": {...},   # Cómo reservar
    "navegacion": {...},        # Navegación del sitio
    "documentos_digitales": {...}, # Formatos y requisitos
    "horarios_atencion": {...}, # Horarios
    "preguntas_frecuentes": [...], # FAQs
    "soporte_tecnico": {...}    # Soporte
}
```

**Funciones:**
- `get_knowledge_context()` - Contexto del sistema para OpenAI
- `search_knowledge(query)` - Búsqueda en knowledge base

### 4. db_models.py
**Modelos de datos SQLModel**

```python
- ChatSession      # Sesiones de conversación
- ChatMessage      # Mensajes individuales
- ChatMetrics      # Métricas de uso
- User             # Referencia a usuarios
```

### 5. config.py
**Configuración centralizada**

```python
class Settings:
    # Base de datos
    DATABASE_URL
    
    # OpenAI
    OPENAI_API_KEY
    OPENAI_MODEL
    OPENAI_MAX_TOKENS
    OPENAI_TEMPERATURE
    
    # Redis
    REDIS_HOST
    REDIS_PORT
    
    # JWT
    SECRET_KEY
    ALGORITHM
    
    # URLs de servicios
    AUTH_SERVICE_URL
    RESERVATIONS_SERVICE_URL
    DOCUMENTS_SERVICE_URL
```

---

## API Endpoints

### POST /chat
**Enviar mensaje al chatbot**

**Autenticación:** Bearer Token requerido

**Request:**
```json
{
  "message": "¿Qué documentos necesito para licencia clase B?",
  "session_id": "uuid-opcional",
  "context": {
    "current_page": "/reservas",
    "section": "reservations",
    "action": "viewing_reservations"
  }
}
```

**Response (200 OK):**
```json
{
  "response": "Para obtener la licencia clase B necesitas:\n1. Cédula de identidad vigente...",
  "session_id": "123e4567-e89b-12d3-a456-426614174000",
  "tokens_used": 245,
  "response_time_ms": 1234,
  "error": null
}
```

**Response (429 - Rate Limit):**
```json
{
  "response": "Lo siento, estamos experimentando un alto volumen de consultas...",
  "session_id": "...",
  "error": "rate_limit"
}
```

**Response (401 Unauthorized):**
```json
{
  "detail": "No se pudo validar las credenciales"
}
```

---

### GET /chat/history/{session_id}
**Obtener historial de conversación**

**Autenticación:** Bearer Token requerido

**Response (200 OK):**
```json
{
  "session_id": "123e4567-e89b-12d3-a456-426614174000",
  "messages": [
    {
      "role": "user",
      "content": "Hola, necesito información",
      "timestamp": "2025-11-09T14:30:00Z",
      "tokens_used": null,
      "response_time_ms": null
    },
    {
      "role": "assistant",
      "content": "¡Hola! ¿En qué puedo ayudarte?",
      "timestamp": "2025-11-09T14:30:01Z",
      "tokens_used": 150,
      "response_time_ms": 1200
    }
  ]
}
```

---

### DELETE /chat/session/{session_id}
**Cerrar/limpiar sesión de chat**

**Autenticación:** Bearer Token requerido

**Response (200 OK):**
```json
{
  "message": "Sesión cerrada exitosamente"
}
```

---

### GET /chat/metrics
**Obtener métricas de uso del usuario**

**Autenticación:** Bearer Token requerido

**Response (200 OK):**
```json
{
  "total_conversations": 5,
  "total_messages": 42,
  "total_tokens": 8540,
  "avg_response_time_ms": 1350.5
}
```

---

### GET /chat/sessions
**Listar sesiones activas del usuario**

**Autenticación:** Bearer Token requerido

**Response (200 OK):**
```json
{
  "sessions": [
    {
      "session_id": "uuid-1",
      "created_at": "2025-11-09T10:00:00Z",
      "updated_at": "2025-11-09T14:30:00Z",
      "is_active": true
    }
  ]
}
```

---

### GET /health
**Healthcheck del servicio**

**No requiere autenticación**

**Response (200 OK):**
```json
{
  "status": "ok",
  "service": "chatbot-ai",
  "version": "1.0.0"
}
```

---

## Base de Datos

### Esquema de Tablas

#### users
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    nombre VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### chat_sessions
```sql
CREATE TABLE chat_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    session_id VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
```

#### chat_messages
```sql
CREATE TABLE chat_messages (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES chat_sessions(id),
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tokens_used INTEGER,
    response_time_ms INTEGER
);
```

#### chat_metrics
```sql
CREATE TABLE chat_metrics (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES chat_sessions(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_messages INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    avg_response_time_ms FLOAT DEFAULT 0.0,
    topics_discussed TEXT DEFAULT '',
    satisfaction_rating INTEGER CHECK (satisfaction_rating >= 1 AND satisfaction_rating <= 5)
);
```

### Vistas

#### user_chat_stats
Estadísticas agregadas por usuario
```sql
SELECT 
    u.id as user_id,
    COUNT(DISTINCT cs.id) as total_sessions,
    COUNT(cm.id) as total_messages,
    SUM(cme.total_tokens) as total_tokens_used,
    AVG(cme.avg_response_time_ms) as avg_response_time,
    MAX(cs.updated_at) as last_interaction
FROM users u
LEFT JOIN chat_sessions cs ON u.id = cs.user_id
...
```

#### daily_chatbot_metrics
Métricas diarias del sistema
```sql
SELECT 
    DATE(date) as metric_date,
    COUNT(DISTINCT user_id) as unique_users,
    COUNT(DISTINCT session_id) as total_sessions,
    SUM(total_messages) as total_messages,
    SUM(total_tokens) as total_tokens,
    AVG(avg_response_time_ms) as avg_response_time
FROM chat_metrics
GROUP BY DATE(date)
```

### Índices Optimizados

```sql
-- Índices en chat_sessions
CREATE INDEX idx_chat_sessions_user_id ON chat_sessions(user_id);
CREATE INDEX idx_chat_sessions_session_id ON chat_sessions(session_id);
CREATE INDEX idx_chat_sessions_is_active ON chat_sessions(is_active);

-- Índices en chat_messages
CREATE INDEX idx_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX idx_chat_messages_timestamp ON chat_messages(timestamp);
CREATE INDEX idx_chat_messages_role ON chat_messages(role);

-- Índices en chat_metrics
CREATE INDEX idx_chat_metrics_user_id ON chat_metrics(user_id);
CREATE INDEX idx_chat_metrics_date ON chat_metrics(date);
CREATE INDEX idx_chat_metrics_session_id ON chat_metrics(session_id);
```

---

## Integración Frontend

### ChatBotWidget Component

**Ubicación:** `services/frontend/src/components/ChatBotWidget.jsx`

**Características:**
- Widget flotante en esquina inferior derecha
- Interfaz moderna con TailwindCSS
- Persistencia de sesión en localStorage
- Detección automática de contexto
- Sugerencias rápidas (FAQs)
- Indicadores de carga (typing animation)
- Manejo de errores visual
- Timestamps en mensajes
- Scroll automático al último mensaje

### Uso en la Aplicación

```jsx
// En App.jsx
import ChatBotWidget from './components/ChatBotWidget';

export default function App() {
  return (
    <Router>
      {/* Rutas de la aplicación */}
      
      {/* ChatBot disponible si hay token */}
      {localStorage.getItem('token') && <ChatBotWidget />}
    </Router>
  );
}
```

### Estados del Widget

1. **Cerrado**: Botón flotante azul con indicador verde
2. **Abierto sin mensajes**: Mensaje de bienvenida + sugerencias rápidas
3. **Conversación activa**: Historial de mensajes
4. **Cargando**: Animación de puntos (typing)
5. **Error**: Mensaje de error en rojo

### Persistencia

```javascript
// Guardar en localStorage
localStorage.setItem('chatbot_session_id', sessionId);
localStorage.setItem('chatbot_messages', JSON.stringify(messages));

// Recuperar al cargar
const savedSessionId = localStorage.getItem('chatbot_session_id');
const savedMessages = JSON.parse(localStorage.getItem('chatbot_messages'));
```

### Detección de Contexto

```javascript
const getCurrentContext = () => {
  const path = window.location.pathname;
  const context = { current_page: path };
  
  if (path.includes('/reservas')) {
    context.section = 'reservations';
  } else if (path.includes('/documentos')) {
    context.section = 'documents';
  }
  
  return context;
};
```

---

## Knowledge Base

### Estructura

La knowledge base está organizada en secciones temáticas:

```python
KNOWLEDGE_BASE = {
    "sistema": {
        "nombre": "...",
        "descripcion": "...",
        "horarios": "..."
    },
    "licencias": {
        "clase_b": { requisitos, costo, duracion },
        "clase_a": { requisitos, costo, duracion },
        "renovacion": { requisitos, costo, nota },
        "duplicado": { requisitos, costo }
    },
    "proceso_reserva": {
        "pasos": [...],
        "cancelacion": "...",
        "consejos": [...]
    },
    # ... más secciones
}
```

### Búsqueda Inteligente

La función `search_knowledge(query)` utiliza palabras clave para encontrar información relevante:

```python
keywords_map = {
    "clase b": ["licencias", "clase_b"],
    "renovar": ["licencias", "renovacion"],
    "reserva": ["proceso_reserva"],
    "documentos": ["documentos_digitales"],
    # ...
}
```

### Expansión de la Knowledge Base

Para agregar nueva información:

1. Editar `knowledge_base.py`
2. Agregar entrada en `KNOWLEDGE_BASE`
3. Actualizar keywords_map en `search_knowledge()`
4. Opcional: Actualizar `get_knowledge_context()` si es información crítica

Ejemplo:
```python
"nueva_seccion": {
    "descripcion": "...",
    "detalles": [...]
}
```

---

## Monitoreo y Métricas

### Métricas Expuestas

El servicio expone métricas en formato compatible con Prometheus:

**Métricas de Aplicación:**
- Número de consultas por minuto
- Tiempo de respuesta promedio
- Tasa de errores (4xx, 5xx)
- Tokens consumidos de OpenAI
- Sesiones activas

**Métricas de Base de Datos:**
- Conexiones activas
- Queries por segundo
- Tamaño de tablas
- Índices utilizados

### Alertas Configuradas

#### 1. ChatBotServicioCaido
```yaml
expr: up{job="services", instance=~"chatbot-service-.*"} == 0
for: 1m
severity: critical
```
Se activa si el servicio no responde por más de 1 minuto.

#### 2. ChatBotTiempoRespuestaAlto
```yaml
expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 5
for: 5m
severity: warning
```
Se activa si el percentil 95 del tiempo de respuesta supera 5 segundos.

#### 3. ChatBotTasaErroresAlta
```yaml
expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
for: 5m
severity: warning
```
Se activa si la tasa de errores 5xx supera el 5%.

#### 4. ChatBotBaseDatosCaida
```yaml
expr: up{job="postgres_exporters", instance="postgres-exporter-chatbot:9187"} == 0
for: 1m
severity: critical
```
Se activa si la base de datos del chatbot no responde.

### Dashboards Grafana

Se recomienda crear dashboards con:

**Panel 1: Consultas por Minuto**
```promql
rate(http_requests_total{job="services", instance=~"chatbot-service-.*"}[1m])
```

**Panel 2: Tiempo de Respuesta P95**
```promql
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

**Panel 3: Tokens Consumidos (Costo)**
```promql
sum(rate(openai_tokens_total[1h]))
```

**Panel 4: Sesiones Activas**
```sql
SELECT COUNT(*) FROM chat_sessions WHERE is_active = true
```

---

## Deployment

### Prerequisitos

1. **Docker y Docker Compose** instalados
2. **OpenAI API Key** válida
3. **Variables de entorno** configuradas

### Variables de Entorno Requeridas

Crear archivo `.env` en la raíz del proyecto:

```env
# ChatBot IA Service
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_MAX_TOKENS=500
OPENAI_TEMPERATURE=0.7

# ChatBot Database
CHATBOT_DB_USER=admin
CHATBOT_DB_PASSWORD=admin
CHATBOT_DB_NAME=chatbot_db
CHATBOT_DB_PORT=5435

# Service Port
CHATBOT_SERVICE_PORT=8005
```

### Despliegue Completo

```bash
# 1. Clonar repositorio
git clone <repo-url>
cd proyecto

# 2. Configurar variables de entorno
cp .env.example .env
# Editar .env y agregar OPENAI_API_KEY

# 3. Construir e iniciar servicios
docker-compose up -d --build

# 4. Verificar que los servicios están corriendo
docker-compose ps

# 5. Ver logs del chatbot
docker-compose logs -f chatbot-service-1
docker-compose logs -f chatbot-service-2

# 6. Verificar salud del servicio
curl http://localhost:8005/health
```

### Despliegue Solo del ChatBot

```bash
# Iniciar solo servicios relacionados al chatbot
docker-compose up -d chatbot-db chatbot-db-replica chatbot-service-1 chatbot-service-2 redis
```

### Verificación Post-Deployment

```bash
# 1. Verificar que la base de datos está inicializada
docker-compose exec chatbot-db psql -U admin -d chatbot_db -c "\dt"

# 2. Verificar replicación
docker-compose exec chatbot-db psql -U admin -d chatbot_db -c "SELECT client_addr, state FROM pg_stat_replication;"

# 3. Probar endpoint de salud
curl http://localhost/api/chatbot/health

# 4. Ver métricas en Prometheus
# Abrir http://localhost:9090
# Query: up{job="services", instance=~"chatbot-service-.*"}

# 5. Ver dashboard en Grafana
# Abrir http://localhost:3001
```

---

## Mantenimiento

### Tareas Rutinarias

#### Revisar Logs Diariamente
```bash
# Últimas 100 líneas
docker-compose logs --tail=100 chatbot-service-1

# Seguir logs en tiempo real
docker-compose logs -f chatbot-service-1
```

#### Monitorear Uso de Tokens (Costos)
```sql
-- Tokens consumidos hoy
SELECT 
    DATE(date) as fecha,
    SUM(total_tokens) as tokens_totales,
    COUNT(DISTINCT user_id) as usuarios_unicos
FROM chat_metrics
WHERE date >= CURRENT_DATE
GROUP BY DATE(date);

-- Costo estimado (GPT-3.5-turbo: ~$0.0015/1K tokens)
SELECT 
    SUM(total_tokens) / 1000.0 * 0.0015 as costo_estimado_usd
FROM chat_metrics
WHERE date >= CURRENT_DATE - INTERVAL '30 days';
```

#### Limpiar Sesiones Antiguas
```sql
-- Marcar como inactivas sesiones de más de 30 días
UPDATE chat_sessions
SET is_active = false
WHERE updated_at < NOW() - INTERVAL '30 days'
  AND is_active = true;
```

#### Backup de Base de Datos
```bash
# Backup manual
docker-compose exec chatbot-db pg_dump -U admin chatbot_db > chatbot_backup_$(date +%Y%m%d).sql

# Restaurar backup
docker-compose exec -T chatbot-db psql -U admin chatbot_db < chatbot_backup_20251109.sql
```

### Actualizar Knowledge Base

1. Editar `services/ai-service/knowledge_base.py`
2. Agregar/modificar información en `KNOWLEDGE_BASE`
3. Reconstruir servicio:
```bash
docker-compose up -d --build chatbot-service-1 chatbot-service-2
```

### Escalar el Servicio

Para agregar más instancias:

1. Editar `docker-compose.yml`:
```yaml
chatbot-service-3:
  build:
    context: ./services/ai-service
  # ... misma configuración que service-1/2
```

2. Actualizar API Gateway:
```nginx
upstream chatbot_cluster {
    server chatbot-service-1:8005;
    server chatbot-service-2:8005;
    server chatbot-service-3:8005;
}
```

3. Reiniciar:
```bash
docker-compose up -d --build
```

### Rotación de API Keys

1. Generar nueva API key en OpenAI
2. Actualizar `.env`:
```env
OPENAI_API_KEY=sk-new-key-here
```
3. Reiniciar servicios:
```bash
docker-compose restart chatbot-service-1 chatbot-service-2
```

---

## Troubleshooting

### Problema: "El chatbot no responde"

**Causas posibles:**
1. API key de OpenAI inválida o sin crédito
2. Servicio caído
3. Base de datos no disponible
4. Rate limit de OpenAI alcanzado

**Solución:**
```bash
# 1. Verificar logs
docker-compose logs chatbot-service-1 | grep -i error

# 2. Verificar salud del servicio
curl http://localhost:8005/health

# 3. Verificar conexión a BD
docker-compose exec chatbot-db psql -U admin -d chatbot_db -c "SELECT 1;"

# 4. Verificar API key en .env
grep OPENAI_API_KEY .env

# 5. Verificar créditos en OpenAI
# Ir a https://platform.openai.com/account/usage

# 6. Reiniciar servicio
docker-compose restart chatbot-service-1 chatbot-service-2
```

### Problema: "Tiempo de respuesta muy alto"

**Causas posibles:**
1. OpenAI API lenta
2. Base de datos sobrecargada
3. Historial de conversación muy largo

**Solución:**
```bash
# 1. Verificar métricas de OpenAI
# Ver dashboard en Grafana

# 2. Optimizar base de datos
docker-compose exec chatbot-db psql -U admin -d chatbot_db -c "VACUUM ANALYZE;"

# 3. Limitar historial de conversación
# Editar config.py: MAX_CONVERSATION_HISTORY = 5

# 4. Reducir temperatura/tokens
# Editar .env:
# OPENAI_MAX_TOKENS=300
# OPENAI_TEMPERATURE=0.5
```

### Problema: "Error 401 en el frontend"

**Causas posibles:**
1. Token expirado
2. SECRET_KEY no coincide con auth-service

**Solución:**
```bash
# 1. Verificar que SECRET_KEY es el mismo
grep SECRET_KEY services/auth-service/.env
grep SECRET_KEY services/ai-service/.env

# 2. Cerrar sesión y volver a iniciar
# En el navegador: localStorage.clear()

# 3. Reiniciar servicios
docker-compose restart auth-service-1 chatbot-service-1
```

### Problema: "Base de datos llena"

**Solución:**
```sql
-- Ver tamaño de tablas
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Eliminar mensajes antiguos (>90 días)
DELETE FROM chat_messages
WHERE timestamp < NOW() - INTERVAL '90 days';

-- Eliminar métricas antiguas (>180 días)
DELETE FROM chat_metrics
WHERE date < NOW() - INTERVAL '180 days';

-- Vacuumar para liberar espacio
VACUUM FULL;
```

### Problema: "Widget no aparece en el frontend"

**Solución:**
```bash
# 1. Verificar que el componente está importado
grep ChatBotWidget services/frontend/src/App.jsx

# 2. Verificar que hay token en localStorage
# En consola del navegador:
# console.log(localStorage.getItem('token'))

# 3. Verificar que la ruta no es /login o /register
# console.log(window.location.pathname)

# 4. Reconstruir frontend
docker-compose up -d --build frontend
```

### Problema: "OpenAI rate limit alcanzado"

**Solución:**
```python
# El servicio ya maneja este error automáticamente
# Responde al usuario con mensaje amigable:
# "Lo siento, estamos experimentando un alto volumen de consultas..."

# Para prevenir:
# 1. Implementar rate limiting por usuario
# 2. Aumentar tier en OpenAI
# 3. Agregar caché de respuestas frecuentes en Redis
```

---

## Contacto y Soporte

Para problemas técnicos o consultas sobre el servicio ChatBot IA:

**Equipo de Desarrollo:**
- Email: desarrollo@proyecto.cl
- Slack: #chatbot-support

**Documentación Adicional:**
- OpenAI API: https://platform.openai.com/docs
- FastAPI: https://fastapi.tiangolo.com
- SQLModel: https://sqlmodel.tiangolo.com

---

**Última actualización:** Noviembre 9, 2025  
**Versión del documento:** 1.0.0  
**Autor:** Equipo de Desarrollo - Proyecto Administración de Redes
