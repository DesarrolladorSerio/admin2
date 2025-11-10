import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Configuración del servicio de ChatBot IA"""
    
    # Base de datos
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://admin:admin@chatbot-db:5432/chatbot_db"
    )
    
    # Ollama Configuration (100% GRATUITO - Sin costos ni API keys)
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "tinyllama")
    OLLAMA_TIMEOUT: int = int(os.getenv("OLLAMA_TIMEOUT", "60"))
    
    # Redis para caché y sesiones
    REDIS_HOST: str = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "1"))
    
    # JWT para autenticación
    SECRET_KEY: str = os.getenv("SECRET_KEY", "un-secreto-muy-fuerte-y-largo")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    
    # URLs de otros servicios
    AUTH_SERVICE_URL: str = os.getenv("AUTH_SERVICE_URL", "http://auth-service-1:8000")
    RESERVATIONS_SERVICE_URL: str = os.getenv("RESERVATIONS_SERVICE_URL", "http://reservations-service-1:8002")
    DOCUMENTS_SERVICE_URL: str = os.getenv("DOCUMENTS_SERVICE_URL", "http://documents-service:8003")
    
    # Configuración del servicio
    PORT: int = int(os.getenv("PORT", "8005"))
    MAX_CONVERSATION_HISTORY: int = 8  # Reducido para ajustarse al contexto de 2048 tokens
    SESSION_TIMEOUT_MINUTES: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
