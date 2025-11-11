# Servicio de Datos Municipalidad

## Descripción
Servicio para gestionar documentos y datos de la municipalidad, incluyendo licitaciones, documentos oficiales y otros archivos institucionales.

## Características
- **Gestión de documentos municipales**: Subida, descarga, eliminación y visualización
- **Tipos de documentos configurables**: Antecedentes generales, estados financieros, experiencia previa, propuestas técnicas y económicas
- **Almacenamiento en MinIO**: Archivos seguros con estructura organizada por usuario y fecha
- **Validación de archivos**: Control de tipos MIME y tamaños máximos
- **Estadísticas**: Métricas de uso y documentos por tipo

## Endpoints Principales

### Documentos
- `GET /document-types` - Obtener tipos de documentos disponibles
- `POST /upload` - Subir un nuevo documento
- `GET /my-documents` - Listar mis documentos
- `GET /document/{id}` - Obtener información de un documento
- `GET /download/{id}` - Descargar un documento
- `GET /preview/{id}` - Vista previa de un documento
- `DELETE /document/{id}` - Eliminar un documento
- `GET /stats` - Estadísticas del usuario

### Sistema
- `GET /health` - Health check del servicio
- `GET /test` - Test de conectividad

## Tecnologías
- **FastAPI**: Framework web Python
- **PostgreSQL**: Base de datos
- **MinIO**: Almacenamiento de objetos
- **SQLModel**: ORM para PostgreSQL

## Variables de Entorno
```env
DATABASE_URL=postgresql+psycopg://user:pass@host:port/db
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_SECURE=false
MINIO_BUCKET=municipalidad-docs
AUTH_SERVICE_URL=http://auth-service-1:8000
SECRET_KEY=your-secret-key
ALGORITHM=HS256
PORT=8006
```

## Uso con Docker Compose
```bash
# Construir e iniciar el servicio
docker-compose up -d datos-municipalidad-service

# Ver logs
docker-compose logs -f datos-municipalidad-service

# Reiniciar servicio
docker-compose restart datos-municipalidad-service
```

## Rutas API Gateway
Las rutas están expuestas a través del API Gateway en:
- `http://localhost:8080/api/municipalidad/*`

## Tipos de Documentos Soportados

### Antecedentes Generales
- Documentos de identificación y constitución
- Requerido: ✅

### Estados Financieros
- Balance y estado de resultados
- Requerido: ✅

### Experiencia Previa
- Certificados de trabajos anteriores
- Requerido: ✅

### Propuesta Técnica
- Documentos técnicos de la propuesta
- Requerido: ✅

### Propuesta Económica
- Oferta económica y presupuesto
- Requerido: ✅

### Documentos Adicionales
- Otros documentos de respaldo
- Requerido: ❌

## Ejemplo de Uso

### Subir un documento
```bash
curl -X POST "http://localhost:8080/api/municipalidad/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@documento.pdf" \
  -F "document_type=Antecedentes Generales" \
  -F "description=Documento de prueba" \
  -F "is_public=false"
```

### Obtener mis documentos
```bash
curl -X GET "http://localhost:8080/api/municipalidad/my-documents" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Descargar un documento
```bash
curl -X GET "http://localhost:8080/api/municipalidad/download/1" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o documento.pdf
```

## Integración con Otros Servicios
- **auth-service**: Autenticación y autorización de usuarios
- **documents-db**: Base de datos compartida con documents-service
- **minio**: Almacenamiento de archivos con bucket propio
- **api-gateway**: Enrutamiento y proxy inverso

## Desarrollo

### Instalar dependencias
```bash
pip install -r requirements.txt
```

### Ejecutar localmente
```bash
uvicorn main:app --host 0.0.0.0 --port 8006 --reload
```

## Seguridad
- Autenticación JWT requerida para todos los endpoints (excepto health)
- Validación de tipos MIME
- Control de tamaño de archivos
- Checksums SHA-256 para integridad

## Monitoreo
El servicio expone métricas básicas:
- Health check: `/health`
- Test de conectividad: `/test`
- Estadísticas de uso: `/stats`
