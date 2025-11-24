# 🚀 Guía Rápida de Inicio - ChatBot IA

## Setup Rápido (5 minutos)

### 1️⃣ Obtener API Key de OpenAI

1. Ir a https://platform.openai.com/api-keys
2. Crear una cuenta o iniciar sesión
3. Click en "Create new secret key"
4. Copiar la key (empieza con `sk-...`)

### 2️⃣ Configurar Variables de Entorno

```bash
# En la raíz del proyecto, editar .env
nano .env
```

Agregar estas líneas:
```env
# ===== ChatBot IA Configuration =====
OPENAI_API_KEY=sk-tu-api-key-aqui
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_MAX_TOKENS=500
OPENAI_TEMPERATURE=0.7

CHATBOT_DB_USER=admin
CHATBOT_DB_PASSWORD=admin
CHATBOT_DB_NAME=chatbot_db
CHATBOT_DB_PORT=5435
CHATBOT_SERVICE_PORT=8005
```

### 3️⃣ Iniciar el Sistema

```bash
# Construir e iniciar todos los servicios
docker-compose up -d --build

# Ver logs del chatbot
docker-compose logs -f chatbot-service-1
```

### 4️⃣ Verificar que Funciona

```bash
# Verificar salud del servicio
curl http://localhost:8005/health

# Debería responder:
# {"status":"ok","service":"chatbot-ai","version":"1.0.0"}
```

### 5️⃣ Probar en el Frontend

1. Abrir navegador: http://localhost:8080
2. Iniciar sesión con tu usuario
3. Verás un botón azul flotante en la esquina inferior derecha 💬
4. Click en el botón
5. ¡Escribe tu primera pregunta!

## Preguntas de Prueba

Prueba estas consultas para validar el chatbot:

```
✅ "¿Qué documentos necesito para licencia clase B?"
✅ "¿Cómo hago una reserva?"
✅ "¿Cuánto cuesta la licencia?"
✅ "¿Cuáles son los horarios de atención?"
✅ "Necesito ayuda para navegar el sistema"
```

## Comandos Útiles

```bash
# Ver todos los servicios corriendo
docker-compose ps

# Ver logs en tiempo real
docker-compose logs -f chatbot-service-1

# Reiniciar el chatbot
docker-compose restart chatbot-service-1 chatbot-service-2

# Detener todo
docker-compose down

# Reiniciar todo desde cero (⚠️ borra datos)
docker-compose down -v
docker-compose up -d --build
```

## Monitoreo

### Prometheus
- URL: http://localhost:9090
- Query de ejemplo: `up{job="services", instance=~"chatbot-service-.*"}`

### Grafana
- URL: http://localhost:3001
- Usuario: `${GRAFANA_ADMIN_USER}` (ver .env)
- Password: `${GRAFANA_ADMIN_PASSWORD}` (ver .env)

## Troubleshooting Rápido

### ❌ "No aparece el botón del chatbot"
```bash
# Verificar que estás logueado y no en /login o /register
# Abrir consola del navegador y ejecutar:
console.log(localStorage.getItem('token'))
```

### ❌ "El chatbot no responde"
```bash
# Ver logs
docker-compose logs chatbot-service-1 | tail -50

# Verificar API key
grep OPENAI_API_KEY .env

# Reiniciar
docker-compose restart chatbot-service-1 chatbot-service-2
```

### ❌ "Error 401 Unauthorized"
```bash
# Verificar que SECRET_KEY coincide entre servicios
grep SECRET_KEY .env

# Limpiar localStorage y volver a iniciar sesión
# En consola del navegador:
localStorage.clear()
```

## Costos Estimados (OpenAI)

Con GPT-3.5-turbo:
- **Costo por consulta**: ~$0.0005 - $0.001 USD
- **100 consultas/día**: ~$3 USD/mes
- **1000 consultas/día**: ~$30 USD/mes

### Monitorear Costos

```sql
-- Conectar a la base de datos
docker-compose exec chatbot-db psql -U admin -d chatbot_db

-- Ver tokens consumidos hoy
SELECT 
    SUM(total_tokens) as tokens_hoy,
    SUM(total_tokens) / 1000.0 * 0.0015 as costo_estimado_usd
FROM chat_metrics
WHERE date >= CURRENT_DATE;

-- Ver tokens del último mes
SELECT 
    DATE(date) as fecha,
    SUM(total_tokens) as tokens,
    SUM(total_tokens) / 1000.0 * 0.0015 as costo_usd
FROM chat_metrics
WHERE date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(date)
ORDER BY fecha DESC;
```

## Próximos Pasos

1. ✅ **Personalizar Knowledge Base**
   - Editar `services/ai-service/knowledge_base.py`
   - Agregar información específica de tu municipalidad

2. ✅ **Configurar Alertas**
   - Revisar `infrastructure/monitoring/alert_rules.yml`
   - Configurar email/Slack en `alertmanager.yml`

3. ✅ **Crear Dashboard en Grafana**
   - Importar dashboard de métricas del chatbot
   - Configurar visualizaciones personalizadas

4. ✅ **Optimizar Costos**
   - Reducir `OPENAI_MAX_TOKENS` si las respuestas son muy largas
   - Implementar caché de respuestas frecuentes
   - Considerar rate limiting por usuario

## Documentación Completa

Para información detallada, consultar:
- 📖 `services/ai-service/README.md` - Documentación del servicio
- 📖 `docs/chatbot-service.md` - Documentación técnica completa

## Soporte

¿Necesitas ayuda?
- 💬 Slack: #chatbot-support
- 📧 Email: desarrollo@proyecto.cl
- 📚 Docs: Ver archivos .md en el proyecto

---

**¡Felicitaciones! Tu ChatBot IA está listo para usar 🎉**
