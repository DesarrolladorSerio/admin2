from pydantic import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Base de datos
    database_url: str = "postgresql://postgres:password@documents-db:5432/documents"
    
    # MinIO
    minio_endpoint: str = "minio:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_secure: bool = False
    minio_bucket: str = "documents"
    
    # Autenticación
    auth_service_url: str = "http://auth-service:8000"
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    
    # Archivos
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    allowed_mime_types: List[str] = [
        "application/pdf",
        "image/jpeg",
        "image/png",
        "image/gif",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "text/plain",
        "application/zip"
    ]
    
    # Tipos de documentos para licitaciones
    document_types: List[dict] = [
        {
            "name": "Antecedentes Generales",
            "description": "Documentos generales de identificación y constitución",
            "category": "general",
            "required": True
        },
        {
            "name": "Estados Financieros",
            "description": "Balance y estado de resultados",
            "category": "financiero",
            "required": True
        },
        {
            "name": "Experiencia Previa",
            "description": "Certificados de trabajos anteriores",
            "category": "experiencia",
            "required": True
        },
        {
            "name": "Propuesta Técnica",
            "description": "Documentos técnicos de la propuesta",
            "category": "tecnico",
            "required": True
        },
        {
            "name": "Propuesta Económica",
            "description": "Oferta económica y presupuesto",
            "category": "economico",
            "required": True
        },
        {
            "name": "Documentos Adicionales",
            "description": "Otros documentos de respaldo",
            "category": "adicional",
            "required": False
        }
    ]
    
    class Config:
        env_file = ".env"

settings = Settings()