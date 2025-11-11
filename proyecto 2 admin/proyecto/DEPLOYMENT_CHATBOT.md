# 🚀 Instrucciones de Deployment - ChatBot IA (100% GRATUITO)

## 🎉 Importante: SIN COSTOS - SIN API KEYS

Este ChatBot es **100% GRATUITO** y funciona completamente en tu infraestructura local:
- ✅ **No necesitas cuenta de OpenAI**
- ✅ **No necesitas API keys externas**
- ✅ **No necesitas tarjeta de crédito**
- ✅ **Sin cargos por uso**
- ✅ **Todo corre localmente con Ollama**

## Prerequisitos

Antes de comenzar, asegúrate de tener:

- ✅ Docker Desktop instalado y corriendo
- ✅ Docker Compose disponible
- ✅ Al menos **4GB de RAM** disponible para Ollama
- ✅ **~5-7GB de espacio en disco** para el modelo de IA
- ✅ Puertos disponibles: 8005, 5435, 11434
- ✅ Conexión a internet (solo para la descarga inicial del modelo)

## Paso 1: Configurar Variables de Entorno

### En Windows (PowerShell)

```powershell
# Navegar a la carpeta del proyecto
cd "c:\Users\bgano\OneDrive\Documentos\Proyecto U2 administracion de redes\admin2\proyecto 2 admin\proyecto"

# Abrir .env con notepad
notepad .env
```

### Agregar estas líneas al archivo .env

```env
# ============================================
# ChatBot IA Configuration (100% GRATUITO)
# ============================================

# Ollama - LLM Local (No requiere API keys ni costos)
OLLAMA_MODEL=llama2
OLLAMA_TIMEOUT=60

# Base de Datos del ChatBot
CHATBOT_DB_USER=admin
CHATBOT_DB_PASSWORD=admin
CHATBOT_DB_NAME=chatbot_db
CHATBOT_DB_PORT=5435

# Puerto del Servicio
CHATBOT_SERVICE_PORT=8005
```

### ✅ Nota Importante

- **NO necesitas ninguna API key**
- El modelo Llama 2 se descargará automáticamente en el primer inicio
- Todo el procesamiento de IA ocurre localmente en Docker

## Paso 2: Verificar Archivos Creados

Ejecutar en PowerShell:

```powershell
# Verificar que todos los archivos del chatbot existen
Get-ChildItem -Recurse -Filter "*chatbot*" | Select-Object FullName

# Debería mostrar:
# - services/ai-service/main.py
# - services/ai-service/chatbot_service.py
# - services/ai-service/knowledge_base.py
# - services/ai-service/Dockerfile
# - infrastructure/postgres/chatbot-init/init.sql
# - Y más archivos...
```

## Paso 3: Construir e Iniciar Servicios

### Opción A: Iniciar TODO el sistema (Recomendado)

```powershell
# Detener servicios existentes
docker-compose down

# Construir e iniciar TODO
docker-compose up -d --build

# Esto iniciará:
# - Ollama (servidor de IA local)
# - Todas las bases de datos (incluyendo chatbot-db)
# - Todos los servicios (incluyendo chatbot-service-1 y 2)
# - API Gateway actualizado
# - Frontend con ChatBot widget
# - Monitoreo (Prometheus, Grafana)
```

⏳ **Nota**: El primer inicio tomará más tiempo (5-15 minutos) porque Ollama descargará el modelo Llama 2 (~4GB). Los siguientes inicios serán instantáneos.

### Opción B: Solo servicios del ChatBot (Más rápido para testing)

```powershell
# Iniciar Ollama primero
docker-compose up -d ollama

# Esperar a que descargue el modelo (solo primera vez)
docker logs -f ollama_service

# Ctrl+C cuando veas "✅ Ollama listo con modelo llama2"

# Luego iniciar servicios del ChatBot
docker-compose up -d --build chatbot-db chatbot-db-replica chatbot-service-1 chatbot-service-2 redis

# Reiniciar Gateway para aplicar nueva configuración
docker-compose restart gateway

# Reiniciar Frontend para aplicar nuevo componente
docker-compose restart frontend
```

## Paso 4: Verificar que Todo Funciona

### 4.1 Ver Estado de Contenedores

```powershell
# Ver todos los servicios
docker-compose ps

# Verificar específicamente el chatbot y Ollama
docker-compose ps | Select-String "chatbot|ollama"

# Debería mostrar:
# ollama_service       running
# chatbot_service_1    running
# chatbot_service_2    running
# chatbot_db_primary   running
# chatbot_db_replica   running
```

### 4.2 Verificar que Ollama descargó el modelo

```powershell
# Ver modelos instalados en Ollama
docker exec ollama_service ollama list

# Debería mostrar:
# NAME      ID              SIZE      MODIFIED
# llama2    78e26419b446    3.8 GB    X minutes ago
```

### 4.3 Ver Logs del ChatBot

```powershell
# Ver logs en tiempo real
docker-compose logs -f chatbot-service-1

# Buscar errores
docker-compose logs chatbot-service-1 | Select-String "error" -CaseSensitive

# Debería mostrar:
# "Servicio de ChatBot IA iniciado correctamente"
# "Tablas de base de datos creadas/verificadas"
# "Conectado a Ollama en http://ollama:11434"
```

### 4.4 Probar Healthcheck

```powershell
# Probar healthcheck directo al servicio
curl http://localhost:8005/health

# Probar healthcheck a través del gateway
curl http://localhost/api/chatbot/health

# Respuesta esperada:
# {"status":"ok","service":"chatbot-ai","version":"1.0.0","model":"llama2"}
```

### 4.5 Probar Ollama directamente

```powershell
# Verificar que Ollama responde
curl http://localhost:11434/api/tags

# Debería devolver JSON con los modelos instalados

# Probar generación de texto
curl http://localhost:11434/api/generate -d "{\"model\":\"llama2\",\"prompt\":\"Hola\"}"
```

### 4.6 Verificar Base de Datos

```powershell
# Conectar a la base de datos
docker-compose exec chatbot-db psql -U admin -d chatbot_db

# Dentro de psql, ejecutar:
\dt

# Debería mostrar:
# public | chat_messages
# public | chat_metrics
# public | chat_sessions
# public | users

# Salir de psql
\q
```

### 4.7 Verificar Replicación

```powershell
# Verificar estado de replicación
docker-compose exec chatbot-db psql -U admin -d chatbot_db -c "SELECT client_addr, state FROM pg_stat_replication;"

# Debería mostrar la réplica conectada
```

## Paso 5: Probar el ChatBot en el Frontend

### 5.1 Abrir el Sistema

1. Abrir navegador en: http://localhost (o http://localhost:8080)
2. Iniciar sesión con tu usuario
   - Email: usuario@test.com
   - Password: tu-contraseña

### 5.2 Verificar el Widget

1. Deberías ver un **botón azul flotante** en la esquina inferior derecha
2. El botón tiene un ícono de chat 💬
3. Hay un **punto verde** animado indicando que está activo

### 5.3 Abrir el Chat

1. Click en el botón azul
2. Debería abrirse una ventana de chat
3. Verás:
   - Header con avatar del bot
   - Mensaje de bienvenida
   - 4 sugerencias rápidas

### 5.4 Enviar Primera Pregunta

1. Click en una sugerencia, por ejemplo:
   - "¿Qué documentos necesito para licencia clase B?"
2. O escribe tu propia pregunta
3. Presiona Enter o click en el botón de envío (➤)
4. Deberías ver:
   - Tu mensaje en azul (derecha)
   - Animación de "escribiendo..." (3 puntos)
   - Respuesta del bot en blanco (izquierda) generada por Llama 2

⏳ **Nota**: La primera respuesta puede tardar 5-10 segundos ya que Ollama debe cargar el modelo en memoria. Las respuestas subsecuentes serán más rápidas (1-3 segundos).

## Paso 6: Monitorear el Servicio

### 6.1 Prometheus

1. Abrir: http://localhost:9090
2. Ir a Status → Targets
3. Buscar: chatbot-service-1 y chatbot-service-2
4. Estado debe ser: **UP** (verde)

### 7.2 Grafana

1. Abrir: http://localhost:3001
2. Login con credenciales del .env
3. Explorar métricas del chatbot

### 7.3 Ver Logs en Tiempo Real

```powershell
# Terminal 1: Logs de servicio 1
docker-compose logs -f chatbot-service-1

# Terminal 2: Logs de servicio 2
docker-compose logs -f chatbot-service-2

# Ver todas las consultas procesadas
docker-compose logs chatbot-service-1 | Select-String "Respuesta generada"
```

## Paso 7: Verificar Uso de Recursos (100% Local - Sin Costos)

### Consultar Estadísticas de Uso

```powershell
# Conectar a la base de datos
docker-compose exec chatbot-db psql -U admin -d chatbot_db

# Ver estadísticas de hoy (sin costos - todo local)
SELECT 
    COUNT(DISTINCT user_id) as usuarios_unicos,
    SUM(total_messages) as mensajes_totales,
    AVG(avg_response_time_ms) as tiempo_promedio_ms
FROM chat_metrics
WHERE date >= CURRENT_DATE;
```

### Verificar Uso de RAM de Ollama

```powershell
# Ver uso de recursos del contenedor Ollama
docker stats ollama_service --no-stream

# Debería mostrar ~2-4GB de RAM en uso cuando está procesando
```

### ✅ Ventajas de la Solución Local

- **$0.00 USD de costos por consulta** (vs OpenAI ~$0.001 por consulta)
- **Sin límites de rate** (puedes hacer infinitas consultas)
- **100% privacidad** (los datos nunca salen de tu servidor)
- **Sin dependencia de internet** (después de la descarga inicial del modelo)

## Troubleshooting

### ❌ Problema: "Error conectando con Ollama"

**Causa**: Servicio Ollama no está corriendo o el modelo no está descargado

**Solución**:
```powershell
# Verificar que Ollama está corriendo
docker ps | Select-String "ollama"

# Ver logs de Ollama
docker logs ollama_service

# Verificar modelos instalados
docker exec ollama_service ollama list

# Si no hay modelos, descargar manualmente:
docker exec ollama_service ollama pull llama2

# Reiniciar servicios del chatbot
docker-compose restart chatbot-service-1 chatbot-service-2
```

### ❌ Problema: Respuestas muy lentas (>30 segundos)

**Causa**: Insuficiente RAM o CPU para Ollama

**Solución**:
```powershell
# Verificar recursos de Docker
docker stats ollama_service --no-stream

# Aumentar recursos en docker-compose.yml:
# En la sección ollama, cambiar:
#   deploy:
#     resources:
#       limits:
#         cpus: "4.0"    # Aumentar de 2.0 a 4.0
#         memory: 8G     # Aumentar de 4G a 8G

# O cambiar a un modelo más ligero:
docker exec ollama_service ollama pull mistral

# Actualizar .env:
# OLLAMA_MODEL=mistral
```

### ❌ Problema: El botón del chat no aparece

**Causa**: Token no válido o usuario no logueado

**Solución**:
```javascript
// Abrir consola del navegador (F12)
console.log(localStorage.getItem('token'))

// Si es null:
// 1. Cerrar sesión
// 2. Volver a iniciar sesión
```

### ❌ Problema: Error 401 Unauthorized

**Causa**: SECRET_KEY no coincide entre servicios

**Solución**:
```powershell
# Verificar que SECRET_KEY es igual en todos los servicios
Get-Content .env | Select-String "SECRET_KEY"

# Reiniciar todos los servicios
docker-compose restart auth-service-1 chatbot-service-1 chatbot-service-2
```

### ❌ Problema: Base de datos no se conecta

**Solución**:
```powershell
# Verificar estado de la BD
docker-compose ps chatbot-db

# Ver logs
docker-compose logs chatbot-db

# Reiniciar si es necesario
docker-compose restart chatbot-db

# Esperar 10 segundos y verificar
Start-Sleep -Seconds 10
curl http://localhost:8005/health
```

### ❌ Problema: "Disk full" al descargar modelo

**Causa**: Insuficiente espacio en disco para el modelo (~5-7GB)

**Solución**:
```powershell
# Verificar espacio disponible
Get-PSDrive C | Select-Object Used,Free

# Limpiar imágenes Docker no usadas
docker system prune -a --volumes

# O usar un modelo más pequeño:
docker exec ollama_service ollama pull phi
# Y actualizar OLLAMA_MODEL=phi en .env
```

## Comandos Útiles

### Reiniciar Solo el ChatBot

```powershell
docker-compose restart chatbot-service-1 chatbot-service-2
```

### Reconstruir ChatBot (después de cambios en código)

```powershell
docker-compose up -d --build chatbot-service-1 chatbot-service-2
```

### Ver Uso de Recursos

```powershell
# CPU y memoria de cada servicio
docker stats chatbot_service_1 chatbot_service_2 chatbot_db_primary
```

### Limpiar y Reiniciar Todo

```powershell
# ⚠️ CUIDADO: Esto borra todos los datos
docker-compose down -v
docker-compose up -d --build
```

### Backup de Datos del ChatBot

```powershell
# Crear backup
docker-compose exec chatbot-db pg_dump -U admin chatbot_db > chatbot_backup_$(Get-Date -Format "yyyyMMdd").sql

# Restaurar backup
Get-Content chatbot_backup_20251109.sql | docker-compose exec -T chatbot-db psql -U admin chatbot_db
```

## Validación Final

Después del deployment, verificar:

- [ ] Servicios corriendo: `docker-compose ps`
- [ ] Healthcheck OK: `curl http://localhost:8005/health`
- [ ] Base de datos creada: `docker-compose exec chatbot-db psql -U admin -d chatbot_db -c "\dt"`
- [ ] Widget visible en frontend
- [ ] Chat responde correctamente
- [ ] No hay errores en logs
- [ ] Prometheus muestra servicios UP
- [ ] Replicación funcionando

## Próximos Pasos

1. ✅ **Monitorear Costos**
   - Revisar dashboard de OpenAI diariamente
   - Consultar métricas en la BD
   - Ajustar `OPENAI_MAX_TOKENS` si es necesario

2. ✅ **Personalizar Knowledge Base**
   - Editar `services/ai-service/knowledge_base.py`
   - Agregar información específica de tu municipalidad
   - Reconstruir servicio

3. ✅ **Configurar Alertas**
   - Editar `infrastructure/monitoring/alertmanager.yml`
   - Configurar email/Slack para notificaciones

4. ✅ **Crear Dashboard en Grafana**
   - Crear dashboard personalizado
   - Agregar paneles de métricas importantes

5. ✅ **Recopilar Feedback**
   - Monitorear consultas frecuentes
   - Mejorar respuestas según feedback
   - Agregar nuevos tópicos a la knowledge base

## Soporte

Si tienes problemas durante el deployment:

1. 📖 Revisar logs: `docker-compose logs chatbot-service-1`
2. 📖 Consultar documentación: `docs/chatbot-service.md`
3. 💬 Slack: #chatbot-support
4. 📧 Email: desarrollo@proyecto.cl

---

**¡Felicitaciones! Tu ChatBot IA está listo para producción 🎉**

**Última actualización**: Noviembre 9, 2025  
**Versión**: 1.0.0
