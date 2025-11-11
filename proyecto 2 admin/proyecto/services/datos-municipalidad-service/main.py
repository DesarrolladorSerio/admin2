import io
import json
import logging
from datetime import datetime
from typing import Optional

import httpx
from auth_utils import get_current_user
from db_documents import documents_db
from fastapi import (
    Depends,
    FastAPI,
    File,
    Form,
    Header,
    HTTPException,
    UploadFile,
    status,
)
from fastapi.responses import StreamingResponse
from storage_service import storage, validate_file_type

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI sin middlewares - Nginx maneja CORS y routing
app = FastAPI(
    title="Documents Service - Sistema Municipal", 
    version="1.0.0",
    description="Servicio de gestión de documentos - CORS manejado por Nginx Gateway"
)

# NOTA: CORS removido - Nginx API Gateway maneja los headers CORS

# =============================================================================
# FUNCIÓN HELPER PARA NOTIFICACIONES
# =============================================================================

async def send_notification(notification_type: str, recipient_email: str, data: dict):
    """Envía notificación al servicio de notificaciones de forma no bloqueante"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.post(
                "http://notifications-service:8004/notifications/send",
                json={
                    "notification_type": notification_type,
                    "recipient_email": recipient_email,
                    "data": data
                }
            )
            logger.info(f"Notificación enviada: {notification_type} a {recipient_email}")
    except Exception as e:
        logger.error(f"Error enviando notificación: {str(e)}")

# =============================================================================
# ENDPOINTS DE SALUD Y CONFIGURACIÓN
# =============================================================================

@app.get("/")
async def root():
    return {
        "message": "Servicio de Documentos - Sistema Municipal de Trámites",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check para monitoreo"""
    try:
        # Verificar conexión a base de datos
        doc_types = documents_db.get_document_types()
        
        # Verificar conexión a MinIO
        storage.client.bucket_exists(storage.bucket_name)
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "database": "connected",
                "storage": "connected"
            },
            "document_types_count": len(doc_types)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Servicio no disponible: {str(e)}"
        )

@app.get("/test")
async def test():
    """Endpoint de prueba simple"""
    return {
        "message": "Servicio de documentos funcionando correctamente",
        "timestamp": datetime.now().isoformat(),
        "status": "ok"
    }

# =============================================================================
# ENDPOINTS DE TIPOS DE DOCUMENTOS
# =============================================================================

@app.get("/document-types")
async def get_document_types():
    """Obtener tipos de documentos disponibles para el usuario"""
    try:
        types = documents_db.get_document_types()
        return {
            "document_types": types,
            "total": len(types)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo tipos de documentos: {str(e)}"
        )

# =============================================================================
# ENDPOINTS DE GESTIÓN DE DOCUMENTOS
# =============================================================================

@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    document_type: str = Form(...),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    is_public: bool = Form(False),
    current_user: dict = Depends(get_current_user)
):
    """
    Subir un nuevo documento al sistema
    Requiere autenticación JWT válida
    """
    user_id = current_user["id"]
    user_email = current_user["email"]
    
    try:
        # Validar tipo de documento
        doc_types = {dt.type_name: dt for dt in documents_db.get_document_types()}
        if document_type not in doc_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipo de documento '{document_type}' no es válido. Tipos disponibles: {list(doc_types.keys())}"
            )
        
        doc_type_info = doc_types[document_type]
        
        # Validar que el archivo no esté vacío
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se seleccionó ningún archivo"
            )
        
        # Leer archivo
        file_content = await file.read()
        file_size = len(file_content)
        
        # Validar tamaño
        max_size = doc_type_info.max_size_mb * 1024 * 1024
        if file_size > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Archivo demasiado grande ({file_size/1024/1024:.1f}MB). Máximo permitido: {doc_type_info.max_size_mb}MB"
            )
        
        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El archivo está vacío"
            )
        
        # Validar tipo de archivo
        allowed_mime_types = doc_type_info.allowed_mime_types
        is_valid, detected_mime_type = validate_file_type(file_content, allowed_mime_types)
        
        if not is_valid:
            allowed_extensions = doc_type_info.allowed_extensions
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipo de archivo no permitido. Detectado: {detected_mime_type}. Permitidos: {', '.join(allowed_extensions)}"
            )
        
        # Subir a MinIO
        file_stream = io.BytesIO(file_content)
        file_path, checksum = storage.upload_file(
            file_stream, 
            file.filename, 
            detected_mime_type, 
            user_id
        )
        
        # Procesar tags
        tag_list = []
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
        
        # Convertir tags a JSON string para guardar en DB
        tags_json = json.dumps(tag_list) if tag_list else None
        
        # Guardar metadatos en base de datos
        document_data = {
            'filename': file_path.split('/')[-1],
            'original_filename': file.filename,
            'file_path': file_path,
            'file_size': file_size,
            'mime_type': detected_mime_type,
            'user_id': user_id,
            'document_type': document_type,
            'description': description or '',
            'tags': tags_json,
            'is_public': is_public,
            'checksum': checksum
        }
        
        document_id = documents_db.create_document(document_data)
        
        # Enviar notificación de documento subido (no bloqueante)
        if user_email:
            try:
                await send_notification(
                    notification_type="document",
                    recipient_email=user_email,
                    data={
                        "user_name": f"Usuario {user_id}",
                        "document_name": file.filename,
                        "document_type": document_type,
                        "status": "uploaded",
                        "upload_date": datetime.now().strftime("%Y-%m-%d %H:%M")
                    }
                )
            except Exception as e:
                logger.error(f"Error enviando notificación de documento: {str(e)}")
        
        return {
            "success": True,
            "message": "Documento subido exitosamente",
            "document": {
                "id": document_id,
                "filename": file.filename,
                "size": file_size,
                "size_mb": round(file_size / 1024 / 1024, 2),
                "type": document_type,
                "mime_type": detected_mime_type,
                "checksum": checksum[:16] + "..."  # Solo mostrar parte del checksum
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno subiendo documento: {str(e)}"
        )

@app.get("/my-documents")
async def get_my_documents(current_user: dict = Depends(get_current_user)):
    """Obtener todos los documentos del usuario actual"""
    user_id = current_user["id"]
    
    try:
        documents = documents_db.get_user_documents(user_id)
        
        # Convertir a dict y agregar información adicional para el frontend
        documents_list = []
        for doc in documents:
            doc_dict = doc.model_dump()  # Convertir DocumentResponse a dict
            doc_dict['size_mb'] = round(doc_dict['file_size'] / 1024 / 1024, 2)
            doc_dict['can_edit'] = True
            doc_dict['can_delete'] = True
            documents_list.append(doc_dict)
        
        return {
            "documents": documents_list,
            "total": len(documents_list),
            "user_id": user_id
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo documentos: {str(e)}"
        )

@app.get("/document/{document_id}")
async def get_document_info(
    document_id: int,
    user_id: Optional[int] = Header(default=2, alias="x-user-id")
):
    """Obtener información detallada de un documento"""
    # Si no viene user_id, usar 2 por defecto
    if user_id is None:
        user_id = 2
    
    try:
        document = documents_db.get_document_by_id(document_id, user_id)
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Documento no encontrado o no tienes permisos para acceder a él"
            )
        
        # Convertir a dict y agregar información adicional
        doc_dict = document.model_dump()
        doc_dict['size_mb'] = round(doc_dict['file_size'] / 1024 / 1024, 2)
        doc_dict['can_edit'] = doc_dict['user_id'] == user_id
        doc_dict['can_delete'] = doc_dict['user_id'] == user_id
        
        return {
            "document": doc_dict
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo información del documento: {str(e)}"
        )

@app.get("/download/{document_id}")
async def download_document(
    document_id: int,
    user_id: Optional[int] = Header(default=2, alias="x-user-id")
):
    """Descargar un documento"""
    # Si no viene user_id, usar 2 por defecto
    if user_id is None:
        user_id = 2
    
    try:
        document = documents_db.get_document_by_id(document_id, user_id)
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Documento no encontrado o no tienes permisos para descargarlo"
            )
        
        # Convertir a dict
        doc_dict = document.model_dump()
        
        # Descargar archivo de MinIO
        file_data = storage.download_file(doc_dict['file_path'])
        
        return StreamingResponse(
            io.BytesIO(file_data),
            media_type=doc_dict['mime_type'],
            headers={
                "Content-Disposition": f"attachment; filename=\"{doc_dict['original_filename']}\"",
                "Content-Length": str(len(file_data))
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error descargando documento: {str(e)}"
        )

@app.get("/preview/{document_id}")
async def preview_document(
    document_id: int,
    user_id: Optional[int] = Header(default=2, alias="x-user-id")
):
    """Obtener URL de previsualización temporal del documento"""
    # Si no viene user_id, usar 2 por defecto
    if user_id is None:
        user_id = 2
    
    try:
        document = documents_db.get_document_by_id(document_id, user_id)
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Documento no encontrado"
            )
        
        # Convertir a dict
        doc_dict = document.model_dump()
        
        # Generar URL firmada válida por 1 hora
        preview_url = storage.get_presigned_url(doc_dict['file_path'])
        
        return {
            "preview_url": preview_url,
            "document_name": doc_dict['original_filename'],
            "mime_type": doc_dict['mime_type'],
            "expires_in": "1 hora"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generando previsualización: {str(e)}"
        )

@app.delete("/document/{document_id}")
async def delete_document(
    document_id: int,
    user_id: Optional[int] = Header(default=2, alias="x-user-id")
):
    """Eliminar un documento del sistema"""
    # Si no viene user_id, usar 2 por defecto
    if user_id is None:
        user_id = 2
    
    try:
        # Obtener información del documento
        document = documents_db.get_document_by_id(document_id, user_id)
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Documento no encontrado"
            )
        
        # Convertir a dict
        doc_dict = document.model_dump()
        
        # Verificar que es el propietario
        if doc_dict['user_id'] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para eliminar este documento"
            )
        
        # Eliminar archivo de MinIO
        storage_success = storage.delete_file(doc_dict['file_path'])
        
        # Eliminar registro de base de datos
        db_success = documents_db.delete_document(document_id, user_id)
        
        if db_success:
            return {
                "success": True,
                "message": "Documento eliminado exitosamente",
                "document_id": document_id,
                "storage_deleted": storage_success
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error eliminando documento de la base de datos"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error eliminando documento: {str(e)}"
        )

# =============================================================================
# ENDPOINTS DE ESTADÍSTICAS
# =============================================================================

@app.get("/stats")
async def get_user_stats(user_id: Optional[int] = Header(default=2, alias="x-user-id")):
    """Obtener estadísticas de documentos del usuario"""
    # Si no viene user_id, usar 2 por defecto
    if user_id is None:
        user_id = 2
    
    try:
        documents = documents_db.get_user_documents(user_id)
        
        # Calcular estadísticas
        total_documents = len(documents)
        total_size = sum(doc['file_size'] for doc in documents)
        total_size_mb = round(total_size / 1024 / 1024, 2)
        
        # Agrupar por tipo
        by_type = {}
        for doc in documents:
            doc_type = doc['document_type']
            if doc_type not in by_type:
                by_type[doc_type] = {
                    'count': 0,
                    'size': 0,
                    'description': doc['type_description']
                }
            by_type[doc_type]['count'] += 1
            by_type[doc_type]['size'] += doc['file_size']
        
        # Convertir tamaños a MB
        for type_info in by_type.values():
            type_info['size_mb'] = round(type_info['size'] / 1024 / 1024, 2)
        
        return {
            "user_id": user_id,
            "summary": {
                "total_documents": total_documents,
                "total_size_bytes": total_size,
                "total_size_mb": total_size_mb
            },
            "by_type": by_type,
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo estadísticas: {str(e)}"
        )

# =============================================================================
# INICIALIZACIÓN
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """Inicialización del servicio"""
    try:
        # Verificar conectividad con MinIO
        storage.init_bucket()
        
        # Inicializar tipos de documentos por defecto
        documents_db.init_default_data()
        
        print("✅ Servicio de Documentos iniciado correctamente")
        print(f"📊 Bucket MinIO: {storage.bucket_name}")
        print("🗄️ Base de datos: Inicializada")
        
    except Exception as e:
        print(f"❌ Error iniciando servicio: {e}")
        raise

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)