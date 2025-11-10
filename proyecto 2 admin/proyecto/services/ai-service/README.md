# 🤖 Servicio de ChatBot IA - Asistente Virtual Inteligente (100% GRATUITO)

## Descripción

Servicio de chatbot inteligente basado en **Ollama** (LLM local) que proporciona soporte y asistencia en tiempo real a los usuarios del sistema de reservas de licencias de conducir. El chatbot reduce la carga de atención presencial y telefónica respondiendo consultas sobre:

- Requisitos y documentación para diferentes tipos de licencias
- Proceso de reserva y navegación del sistema
- Horarios de atención y políticas
- Resolución de problemas técnicos básicos
- Preguntas frecuentes

> **✅ IMPORTANTE**: Este servicio es **100% GRATUITO** - No requiere API keys externas ni costos por uso. Utiliza modelos de IA ejecutándose localmente en Docker con Ollama.

## Características Principales

### 🎯 Funcionalidades
- **Conversaciones Contextuales**: Mantiene el contexto de la conversación usando sesiones persistentes
- **Knowledge Base Integrada**: Base de conocimientos sobre trámites, licencias y procedimientos
- **Respuestas Inteligentes**: Utiliza modelos LLM locales (Llama 2, Mistral) para respuestas naturales y precisas
- **Detección de Contexto**: Detecta en qué sección del sistema está el usuario para respuestas más relevantes
- **Historial Persistente**: Guarda el historial de conversaciones en base de datos
- **Métricas de Uso**: Recopila estadísticas de uso y rendimiento
- **🆓 Sin Costos**: Corre completamente en tu infraestructura sin costos de API externa

### 🏗️ Arquitectura
- **Alta Disponibilidad**: 2 instancias del servicio con balanceo de carga
- **Base de Datos Replicada**: PostgreSQL con replicación primario-réplica
- **Caché con Redis**: Sesiones y respuestas cacheadas para mejor rendimiento
- **API RESTful**: Endpoints bien documentados con FastAPI
- **Ollama Local**: Servidor de IA ejecutándose en contenedor Docker

## Endpoints de la API

### `POST /chat`
Enviar un mensaje al chatbot y recibir respuesta

**Request:**
```json
{
  "message": "¿Qué documentos necesito para licencia clase B?",
  "session_id": "uuid-opcional",
  "context": {
    "current_page": "/reservas",
    "section": "reservations"
  }
}
```

**Response:**
```json
{
  "response": "Para obtener la licencia clase B necesitas...",
  "session_id": "123e4567-e89b-12d3-a456-426614174000",
  "tokens_used": 245,
  "response_time_ms": 1234
}
```

### `GET /chat/history/{session_id}`
Obtener historial completo de una sesión

### `DELETE /chat/session/{session_id}`
Cerrar/limpiar una sesión de chat

### `GET /chat/metrics`
Obtener métricas de uso del usuario actual

### `GET /chat/sessions`
Listar todas las sesiones activas del usuario

### `GET /health`
Healthcheck del servicio

## Configuración

### Variables de Entorno Requeridas

```env
# ============================================================
# Ollama Configuration (100% GRATUITO - Sin API keys ni costos)
# ============================================================
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=llama2  # Opciones: llama2, mistral, codellama
OLLAMA_TIMEOUT=60

# Base de Datos
CHATBOT_DB_USER=admin
CHATBOT_DB_PASSWORD=admin
CHATBOT_DB_NAME=chatbot_db
CHATBOT_DB_PORT=5435

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=1

# JWT (debe coincidir con auth-service)
SECRET_KEY=un-secreto-muy-fuerte-y-largo
ALGORITHM=HS256

# Servicio
CHATBOT_SERVICE_PORT=8005
```

## Instalación y Uso

### Con Docker Compose (Recomendado)

El servicio se despliega automáticamente con el stack completo:

```bash
docker-compose up -d --build
```

**Nota importante**: En el primer inicio, Ollama descargará automáticamente el modelo Llama 2 (~4GB). Esto puede tardar varios minutos dependiendo de tu conexión a internet.

### Verificar que Ollama está funcionando

```bash
# Verificar modelos instalados
docker exec ollama_service ollama list

# Descargar modelo adicional (opcional)
docker exec ollama_service ollama pull mistral
```

### Modelos Disponibles

Puedes usar diferentes modelos según tus necesidades:
- **llama2** (recomendado): Modelo general de ~4GB
- **mistral**: Modelo más ligero y rápido
- **codellama**: Especializado en código

Para cambiar el modelo, actualiza la variable `OLLAMA_MODEL` en tu `.env`

### Desarrollo Local

```bash
cd services/ai-service

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Nota: No necesitas configurar API keys - es 100% local

# Asegúrate de que Ollama esté corriendo
docker-compose up -d ollama

# Ejecutar servicio
python main.py
```

El servicio estará disponible en `http://localhost:8005`

## Base de Datos

### Esquema

- **users**: Referencia a usuarios del sistema
- **chat_sessions**: Sesiones de conversación
- **chat_messages**: Mensajes individuales (usuario y asistente)
- **chat_metrics**: Métricas de uso y rendimiento

### Vistas
- **user_chat_stats**: Estadísticas agregadas por usuario
- **daily_chatbot_metrics**: Métricas diarias del sistema

## Knowledge Base

El chatbot cuenta con una base de conocimientos estructurada que incluye:

### Licencias
- Clase B (particular)
- Clase A (profesional)
- Renovación
- Duplicado

### Información por Licencia
- Requisitos y documentos necesarios
- Costos y duración del trámite
- Restricciones de edad
- Documentación digital aceptada

### Procedimientos
- Proceso de reserva paso a paso
- Navegación del sistema
- Políticas de cancelación y reprogramación
- Horarios de atención

### Soporte Técnico
- Problemas comunes y soluciones
- Información de contacto
- Formatos de archivos aceptados

## Integración con Frontend

El ChatBot está integrado como un widget flotante disponible en todas las páginas del sistema (excepto login/register).

### Características del Widget
- **Posición Flotante**: Botón en esquina inferior derecha
- **Interfaz Moderna**: Diseño limpio y responsivo
- **Persistencia**: Historial guardado en localStorage
- **Contexto Automático**: Detecta la página actual del usuario
- **Sugerencias Rápidas**: Preguntas frecuentes predefinidas
- **Indicadores Visuales**: Loading states y mensajes de error

### Uso desde el Código

```jsx
import ChatBotWidget from './components/ChatBotWidget';

function App() {
  return (
    <div>
      {/* Tu aplicación */}
      <ChatBotWidget />
    </div>
  );
}
```

## Monitoreo

### Métricas Disponibles
- Número de conversaciones por usuario
- Mensajes totales procesados
- Tokens consumidos (costo)
- Tiempo promedio de respuesta
- Tasa de errores

### Integración con Prometheus

El servicio expone métricas en formato compatible con Prometheus:

```yaml
# En prometheus.yml
scrape_configs:
  - job_name: 'chatbot-service'
    static_configs:
      - targets: ['chatbot-service-1:8005', 'chatbot-service-2:8005']
```

## 🆓 Costos (100% GRATUITO)

### Sin Costos de API Externa
- **✅ Modelo**: Llama 2 / Mistral (ejecutándose localmente)
- **✅ Costo por consulta**: $0.00 USD (completamente gratis)
- **✅ Sin límites de tokens**: No hay cargos por uso
- **✅ Sin facturación externa**: Todo corre en tu infraestructura

### Únicos Requisitos
- **Hardware**: ~4GB de RAM para el modelo (ya incluido en docker-compose.yml)
- **Disco**: ~4-7GB para almacenar el modelo Llama 2
- **CPU**: Al menos 2 cores recomendado (configurable en docker-compose.yml)

### Comparación con OpenAI
| Aspecto | Ollama (Esta solución) | OpenAI GPT |
|---------|----------------------|------------|
| Costo por consulta | **$0.00** | $0.0005 - $0.001 |
| Requiere API Key | **No** | Sí |
| Requiere tarjeta de crédito | **No** | Sí |
| Límites de rate | **Ninguno** | Sí (depende del plan) |
| Privacidad de datos | **100% local** | Enviado a OpenAI |
| Dependencia de internet | **Solo descarga inicial del modelo** | Siempre requiere conexión |

## Troubleshooting

### El chatbot no responde
1. Verificar que Ollama está corriendo: `docker ps | grep ollama`
2. Revisar logs: `docker logs chatbot_service_1`
3. Verificar que el modelo está descargado: `docker exec ollama_service ollama list`
4. Si el modelo no está, descargarlo: `docker exec ollama_service ollama pull llama2`

### Error de conexión con Ollama
- Verificar que el contenedor ollama está saludable: `docker ps`
- Comprobar que OLLAMA_BASE_URL apunta a `http://ollama:11434`
- Revisar logs de Ollama: `docker logs ollama_service`

### El modelo se descarga muy lento
- La descarga inicial de ~4GB puede tardar dependiendo de tu conexión
- El modelo se descarga solo la primera vez
- Puedes pre-descargar el modelo manualmente antes de iniciar los servicios

### Error 401 en el frontend
- Verificar que el usuario tiene un token válido
- Comprobar que SECRET_KEY coincide con auth-service

### Base de datos no se conecta
- Verificar que chatbot-db está saludable: `docker ps`
- Revisar credenciales en variables de entorno
- Comprobar conectividad de red

## Desarrollo y Extensiones

### Agregar Nuevos Tópicos a la Knowledge Base

Editar `knowledge_base.py` y agregar información en la estructura `KNOWLEDGE_BASE`:

```python
KNOWLEDGE_BASE = {
    "nuevo_topico": {
        "descripcion": "...",
        "detalles": [...]
    }
}
```

### Personalizar Respuestas del Bot

Modificar el contexto del sistema en `get_knowledge_context()`:

```python
def get_knowledge_context() -> str:
    context = """
    Eres un asistente... [personalizar tono y comportamiento]
    """
    return context
```

### Agregar Nuevos Endpoints

En `main.py`, agregar nuevas rutas siguiendo el patrón:

```python
@app.post("/custom-endpoint")
async def custom_endpoint(
    data: CustomModel,
    user_data: dict = Depends(verify_token),
    db: Session = Depends(get_session)
):
    # Lógica personalizada
    pass
```

## Seguridad

- ✅ Autenticación JWT requerida para todos los endpoints
- ✅ Validación de permisos por usuario
- ✅ Rate limiting en OpenAI (manejo de errores 429)
- ✅ Sanitización de inputs
- ✅ Logs de auditoría de conversaciones
- ✅ Datos sensibles no se envían a OpenAI

## Contribuir

Para contribuir al desarrollo del chatbot:

1. Crear rama feature: `git checkout -b feature/nueva-funcionalidad`
2. Implementar cambios y tests
3. Documentar en este README
4. Crear Pull Request

## Licencia

Proyecto académico - Universidad [Nombre] - 2025

---

**Desarrollado con ❤️ para mejorar la experiencia del usuario**

