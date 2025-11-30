from minio import Minio
from minio.error import S3Error
import os
from datetime import datetime, timedelta
import uuid
import logging
from typing import Optional, BinaryIO
import magic
import hashlib
import json
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MinIOStorage:
    def __init__(self):
        self.client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure
        )
        self.bucket_name = settings.minio_bucket
        self.init_bucket()
    
    def init_bucket(self):
        """Crear el bucket si no existe"""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"Bucket '{self.bucket_name}' creado")
            else:
                logger.info(f"Bucket '{self.bucket_name}' ya existe")
        except S3Error as e:
            logger.error(f"Error configurando MinIO bucket: {e}")
            raise
    
    def upload_file(self, file_data: BinaryIO, filename: str, content_type: str, user_id: int) -> tuple[str, str]:
        """Subir un archivo a MinIO y retornar path y checksum"""
        try:
            # Leer contenido para calcular checksum
            file_content = file_data.read()
            file_data.seek(0)  # Volver al inicio
            
            # Calcular checksum
            checksum = hashlib.sha256(file_content).hexdigest()
            
            # Generar nombre único para el archivo
            file_extension = filename.split('.')[-1] if '.' in filename else ''
            unique_filename = f"{uuid.uuid4()}.{file_extension}" if file_extension else str(uuid.uuid4())
            
            # Crear estructura de carpetas: usuario/año/mes/archivo
            date_path = datetime.now().strftime("%Y/%m")
            object_name = f"user_{user_id}/{date_path}/{unique_filename}"
            
            # Metadatos del archivo
            metadata = {
                'X-User-ID': str(user_id),
                'X-Original-Filename': filename,
                'X-Upload-Date': datetime.now().isoformat(),
                'X-Checksum': checksum
            }
            
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                data=file_data,
                length=len(file_content),
                content_type=content_type,
                metadata=metadata
            )
            
            logger.info(f"Archivo subido: {object_name}")
            return object_name, checksum
            
        except S3Error as e:
            logger.error(f"Error subiendo archivo a MinIO: {e}")
            raise
    
    def download_file(self, object_name: str) -> bytes:
        """Descargar un archivo de MinIO"""
        try:
            response = self.client.get_object(self.bucket_name, object_name)
            data = response.read()
            response.close()
            response.release_conn()
            return data
        except S3Error as e:
            logger.error(f"Error descargando archivo: {e}")
            raise
    
    def delete_file(self, object_name: str) -> bool:
        """Eliminar un archivo de MinIO"""
        try:
            self.client.remove_object(self.bucket_name, object_name)
            logger.info(f"Archivo eliminado: {object_name}")
            return True
        except S3Error as e:
            logger.error(f"Error eliminando archivo: {e}")
            return False
    
    def get_presigned_url(self, object_name: str, expires: timedelta = timedelta(hours=1)) -> str:
        """Generar URL firmada para acceso temporal"""
        try:
            url = self.client.presigned_get_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                expires=expires
            )
            return url
        except S3Error as e:
            logger.error(f"Error generando URL firmada: {e}")
            raise
    
    def get_file_info(self, object_name: str) -> Optional[dict]:
        """Obtener información de un archivo"""
        try:
            stat = self.client.stat_object(self.bucket_name, object_name)
            return {
                'size': stat.size,
                'etag': stat.etag,
                'last_modified': stat.last_modified,
                'content_type': stat.content_type,
                'metadata': stat.metadata
            }
        except S3Error as e:
            logger.error(f"Error obteniendo info del archivo: {e}")
            return None

# Instancia global
storage = MinIOStorage()

def validate_file_type(file_content: bytes, allowed_mime_types: list) -> tuple[bool, str]:
    """Validar el tipo de archivo basado en su contenido"""
    try:
        # Detectar tipo MIME real del archivo
        mime_type = magic.from_buffer(file_content, mime=True)
        
        # Verificar si está en la lista de tipos permitidos
        is_valid = mime_type in allowed_mime_types
        
        return is_valid, mime_type
    except Exception as e:
        logger.error(f"Error validando tipo de archivo: {e}")
        return False, 'application/octet-stream'

def calculate_file_checksum(file_content: bytes) -> str:
    """Calcular checksum SHA256 de un archivo"""
    return hashlib.sha256(file_content).hexdigest()

def get_file_extension_from_mime(mime_type: str) -> str:
    """Obtener extensión de archivo desde tipo MIME"""
    mime_to_ext = {
        'application/pdf': 'pdf',
        'image/jpeg': 'jpg',
        'image/png': 'png',
        'image/gif': 'gif',
        'application/msword': 'doc',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
        'application/vnd.ms-excel': 'xls',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'xlsx',
        'text/plain': 'txt',
        'application/zip': 'zip'
    }
    return mime_to_ext.get(mime_type, 'bin')