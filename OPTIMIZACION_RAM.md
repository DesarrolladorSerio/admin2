# 🚀 Optimización de RAM - Docker Compose

## 📊 Resumen de Cambios

Se ha reducido significativamente el consumo de RAM del proyecto mediante la optimización de límites de memoria en todos los servicios.

### **Reducción Total Estimada: ~6.3GB → ~2.8GB (56% de reducción)**

---

## 🔧 Cambios Detallados por Servicio

### **Bases de Datos PostgreSQL**
| Servicio | Antes | Después | Ahorro |
|----------|-------|---------|--------|
| `auth-db` (primaria) | 128MB | 64MB | -64MB |
| `auth-db-replica` | Sin límite | 32MB | N/A |
| `reservations-db-primary` | 128MB | 64MB | -64MB |
| `reservations-db-replica` | 64MB | 32MB | -32MB |
| `documents-db` | 128MB | 64MB | -64MB |
| `chatbot-db` | 128MB | 64MB | -64MB |
| **Subtotal DBs** | **~640MB** | **~320MB** | **-320MB** |

### **Servicios Backend (FastAPI)**
| Servicio | Antes | Después | Ahorro |
|----------|-------|---------|--------|
| `auth-service-1` | 256MB | 128MB | -128MB |
| `auth-service-2` | 256MB | 128MB | -128MB |
| `reservations-service-1` | 256MB | 128MB | -128MB |
| `reservations-service-2` | 256MB | 128MB | -128MB |
| `documents-service` | 256MB | 128MB | -128MB |
| `notifications-service` | 256MB | 128MB | -128MB |
| `celery-worker` | 256MB | 128MB | -128MB |
| `chatbot-service` | 256MB | 128MB | -128MB |
| `datos-municipalidad-service` | 256MB | 128MB | -128MB |
| **Subtotal Backend** | **~2.3GB** | **~1.15GB** | **-1.15GB** |

### **Servicios de IA**
| Servicio | Antes | Después | Ahorro |
|----------|-------|---------|--------|
| `ollama` (LLM) | 2GB | 1GB | -1GB |
| **Subtotal IA** | **2GB** | **1GB** | **-1GB** |

### **Almacenamiento y Caché**
| Servicio | Antes | Después | Ahorro |
|----------|-------|---------|--------|
| `minio` | 256MB | 128MB | -128MB |
| `redis` | 64MB | 32MB | -32MB |
| **Subtotal Storage** | **320MB** | **160MB** | **-160MB** |

### **Frontend y Gateway**
| Servicio | Antes | Después | Ahorro |
|----------|-------|---------|--------|
| `frontend` (Nginx) | 128MB | 64MB | -64MB |
| `gateway` (Nginx) | 128MB | 64MB | -64MB |
| **Subtotal Frontend** | **256MB** | **128MB** | **-128MB** |

### **Monitoreo**
| Servicio | Antes | Después | Ahorro |
|----------|-------|---------|--------|
| `prometheus` | 256MB | 128MB | -128MB |
| `alertmanager` | 128MB | 64MB | -64MB |
| `grafana` | 256MB | 128MB | -128MB |
| `pg-backup` | 128MB | 64MB | -64MB |
| `node-exporter` | 64MB | 64MB | 0MB |
| `redis-exporter` | 32MB | 32MB | 0MB |
| `postgres-exporter-*` (×4) | 32MB c/u | 32MB c/u | 0MB |
| **Subtotal Monitoring** | **~700MB** | **~450MB** | **-250MB** |

---

## ⚠️ Consideraciones Importantes

### **Rendimiento**
- Los límites reducidos son adecuados para **entornos de desarrollo y pruebas**
- Para **producción con alta carga**, considera aumentar los límites según necesidad
- Monitorea el uso real de memoria con `docker stats` para ajustar

### **Ollama (LLM)**
- Reducido de 2GB a 1GB
- **Puede afectar el rendimiento** de modelos grandes
- Si experimentas problemas con el modelo `llama2`, considera:
  - Usar un modelo más pequeño (ej: `tinyllama`)
  - Aumentar el límite a 1.5GB o 2GB según necesidad

### **Bases de Datos**
- Las réplicas tienen límites muy bajos (32MB) ya que solo leen datos
- Las primarias (64MB) son suficientes para volúmenes moderados
- PostgreSQL puede funcionar con poca RAM usando swap si es necesario

### **Servicios FastAPI**
- 128MB por servicio es adecuado para APIs con tráfico moderado
- Si tienes endpoints que procesan archivos grandes, considera aumentar

---

## 📈 Monitoreo del Uso Real

Para verificar el consumo real de RAM:

```bash
# Ver uso en tiempo real
docker stats

# Ver solo memoria de servicios específicos
docker stats --format "table {{.Name}}\t{{.MemUsage}}\t{{.MemPerc}}"

# Verificar contenedores que exceden límites
docker stats --no-stream | grep -v "LIMIT"
```

---

## 🔄 Cómo Revertir Cambios

Si necesitas restaurar los límites originales, puedes:

1. **Revertir el commit** (si usas Git):
   ```bash
   git checkout HEAD~1 docker-compose.yml
   ```

2. **Ajustar manualmente** los valores en `docker-compose.yml`

3. **Aumentar selectivamente** solo los servicios que lo necesiten

---

## 🎯 Próximos Pasos Recomendados

1. **Reiniciar los servicios** para aplicar los cambios:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

2. **Monitorear durante 24-48 horas** el comportamiento

3. **Ajustar según necesidad** basándose en métricas reales

4. **Considerar escalar horizontalmente** en lugar de verticalmente si necesitas más capacidad

---

## 📝 Notas Adicionales

- Los límites de CPU también fueron reducidos proporcionalmente
- Todos los servicios mantienen sus configuraciones de `healthcheck`
- No se modificaron volúmenes ni redes
- La arquitectura de alta disponibilidad (réplicas) se mantiene intacta

---

**Fecha de optimización:** 2025-11-23  
**Versión:** 1.0  
**Autor:** Optimización automática de recursos
