from pydantic_settings import BaseSettings
from typing import List
import os

def get_secret(secret_name, default=None):
    file_env = f"{secret_name.upper()}_FILE"
    file_path = os.getenv(file_env)
    if file_path and os.path.exists(file_path):
        with open(file_path, "r") as f:
            return f.read().strip()
    return os.getenv(secret_name.upper(), default)

def get_db_url():
    password_file = os.getenv("DATABASE_URL_FILE")
    if password_file and os.path.exists(password_file):
        with open(password_file, "r") as f:
            password = f.read().strip()
        host = os.getenv("DB_HOST", "documents-db")
        db_name = os.getenv("DB_NAME", "documents")
        user = os.getenv("DB_USER", "app_user")
        return f"postgresql://{user}:{password}@{host}:5432/{db_name}"
    
    return os.getenv("DATABASE_URL", "postgresql://postgres:password@documents-db:5432/documents")

class Settings(BaseSettings):
    # Base de datos
    database_url: str = get_db_url()
    
    # MinIO
    minio_endpoint: str = "minio:9000"
    minio_access_key: str = get_secret("minio_access_key", "minioadmin")
    minio_secret_key: str = get_secret("minio_secret_key", "minioadmin")
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