# 🔧 Solución de Problemas y Optimizaciones

## ❗ Problemas Detectados y Solucionados

### 1. **Error de Replicación de PostgreSQL** ✅

**Problema:**
```
pg_basebackup: error: connection to server at "auth-db" (172.28.0.2), port 5432 failed: 
FATAL: no pg_hba.conf entry for replication connection from host "172.28.0.5", user "replicator", no encryption
```

**Causa:** 
Las bases de datos primarias no tenían configurado `pg_hba.conf` para permitir conexiones de replicación.

**Solución Aplicada:**
Se crearon scripts de inicialización:
- `infrastructure/postgres/auth-init/02-setup-replication.sh`
- `infrastructure/postgres/reservations-init/02-setup-replication.sh`

Estos scripts configuran automáticamente:
- `pg_hba.conf` para permitir replicación desde la red Docker (172.28.0.0/16)
- `postgresql.conf` con parámetros de replicación necesarios

**Cómo Aplicar:**
```bash
# Eliminar volúmenes de las bases de datos para forzar reinicialización
docker-compose down
docker volume rm proyecto_auth_primary_data proyecto_auth_replica_data
docker volume rm proyecto_reservations_primary_data proyecto_reservations_replica_data

# Reiniciar servicios
docker-compose up -d
```

---

## 🚀 Optimizaciones de RAM Implementadas

### 2. **ChatBot IA - Reducción Drástica de RAM** ✅

#### Cambios Realizados:

#### A) **Modelo de IA más Eficiente**
- **Antes:** `llama2` (3.8GB de RAM)
- **Después:** `tinyllama` (~400MB de RAM)
- **Ahorro:** ~3.4GB de RAM (89% menos)

#### B) **Contexto Limitado**
```python
# knowledge_base.py - contexto reducido de ~2000 a ~800 caracteres
# Alcance estricto: solo licencias de conducir
```

Restricciones implementadas:
- ✅ Solo responde sobre licencias de conducir
- ✅ Rechaza consultas generales (noticias, código, matemáticas, etc.)
- ✅ Máximo 3 párrafos por respuesta
- ✅ Contacto con soporte para temas fuera de alcance

#### C) **Parámetros de Generación Optimizados**
```python
# chatbot_service.py
{
    'num_predict': 150,    # Reducido de 500 (70% menos tokens)
    'num_ctx': 1024,       # Reducido de 2048 (50% menos contexto)
}
```

#### D) **Historial Reducido**
- **Antes:** Últimos 8 mensajes
- **Después:** Últimos 4 mensajes
- **Beneficio:** Menos RAM y procesamiento

### Resultado Total de Optimización de Chatbot:
- **RAM del modelo:** llama2 (3.8GB) → tinyllama (400MB) = -3.4GB
- **RAM en ejecución:** Contexto reducido = -200MB aprox
- **Total ahorrado:** ~3.6GB de RAM

---

## 📊 Resumen General de RAM

| Componente | Antes | Después | Ahorro |
|------------|-------|---------|--------|
| **Ollama (IA)** | 2GB | 1GB | -1GB |
| **Modelo IA (llama2→tinyllama)** | ~3.8GB | ~400MB | ~-3.4GB |
| **Bases de Datos** | 640MB | 320MB | -320MB |
| **Servicios Backend** | 2.3GB | 1.15GB | -1.15GB |
| **Storage (MinIO+Redis)** | 320MB | 160MB | -160MB |
| **Frontend/Gateway** | 256MB | 128MB | -128MB |
| **Monitoring** | 700MB | 450MB | -250MB |
| **TOTAL ESTIMADO** | **~10GB** | **~3.1GB** | **~7GB (70%)** |

---

## ✅ Instrucciones de Despliegue

### Paso 1: Limpiar Volúmenes Problemáticos

```bash
# Detener todos los servicios
docker-compose down

# Eliminar volúmenes específicos de PostgreSQL para forzar reinicialización
docker volume rm proyecto_auth_primary_data
docker volume rm proyecto_auth_replica_data
docker volume rm proyecto_reservations_primary_data
docker volume rm proyecto_reservations_replica_data

# Opcional: Eliminar modelos de Ollama antiguos para descargar tinyllama
docker volume rm proyecto_ollama_models
```

### Paso 2: Iniciar Servicios

```bash
# Reconstruir imágenes (si es necesario)
docker-compose build

# Iniciar todos los servicios
docker-compose up -d

# Ver logs del chatbot-service y ollama
docker-compose logs -f ollama chatbot-service
```

### Paso 3: Verificar Estado

```bash
# Ver todos los contenedores
docker ps

# Verificar que las réplicas estén funcionando
docker exec auth_db_primary psql -U admin -d auth_db -c "SELECT client_addr,state,sync_state FROM pg_stat_replication;"
docker exec reservations_db_primary psql -U admin -d reservations_db -c "SELECT client_addr,state,sync_state FROM pg_stat_replication;"

# Verificar modelo de Ollama
docker exec ollama_service ollama list
```

### Paso 4: Monitorear RAM

```powershell
# En Windows PowerShell
.\monitor-ram.ps1

# O simplemente
docker stats
```

---

## 🧪 Prueba del ChatBot Optimizado

### Preguntas que SÍ responde:
- ¿Cuáles son los requisitos para licencia clase B?
- ¿Cómo hago una reserva?
- ¿Cuánto cuesta la renovación?
- ¿Qué documentos necesito?
- ¿Cuáles son los horarios de atención?

### Preguntas que NO responde (fuera de alcance):
- ¿Cuál es la capital de Francia?
- ¿Cómo programo en Python?
- ¿Qué tiempo hará mañana?

**Respuesta esperada para fuera de alcance:**
> "Solo puedo ayudar con consultas sobre licencias de conducir y el sistema de reservas. Contacta soporte: soporte@municipalidad.cl"

---

## 🔍 Troubleshooting

### Si Ollama no descarga tinyllama:
```bash
docker exec -it ollama_service bash
ollama pull tinyllama
exit
docker-compose restart chatbot-service
```

### Si las réplicas siguen fallando:
```bash
# Verificar logs detallados
docker logs auth_db_replica
docker logs reservations_db_replica

# Verificar configuración de replicación en primaria
docker exec auth_db_primary cat /var/lib/postgresql/data/pg_hba.conf | grep replication
```

### Si el chatbot responde lento:
- Verificar que esté usando tinyllama: `docker exec ollama_service ollama list`
- Revisar RAM disponible: `docker stats ollama_service`
- Considerar aumentar `num_predict` si las respuestas son muy cortas

---

## 📝 Notas Finales

1. **Tinyllama vs Llama2:**
   - Tinyllama es más rápido pero menos preciso
   - Ideal para consultas simples y específicas
   - Si necesitas respuestas más elaboradas, puedes volver a llama2 editando la variable `OLLAMA_MODEL`

2. **Producción:**
   - Estos límites de RAM son para desarrollo/pruebas
   - Para producción, monitorea durante 1 semana y ajusta según métricas reales

3. **Escalabilidad:**
   - Si necesitas más capacidad, escala horizontalmente (más instancias)
   - No subas todos los límites de RAM simultáneamente

---

**Fecha:** 2025-11-23  
**Autor:** Optimización de Sistema  
**Versión:** 2.0 - Solución completa de replicación + optimización de IA
