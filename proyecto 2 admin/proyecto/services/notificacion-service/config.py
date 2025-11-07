from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Configuración del servicio de notificaciones"""
    
    # Aplicación
    APP_NAME: str = "Servicio de Notificaciones"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # SMTP Email Configuration
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = ""
    SMTP_FROM_NAME: str = "Sistema de Reservas"
    SMTP_TLS: bool = True
    SMTP_SSL: bool = False
    
    # Redis/Queue Configuration
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/0"
    
    # URLs de otros servicios
    AUTH_SERVICE_URL: str = "http://auth-service:8000"
    RESERVATIONS_SERVICE_URL: str = "http://reservations-service:8000"
    DOCUMENTS_SERVICE_URL: str = "http://documents-service:8003"
    
    # JWT Configuration (para validar tokens si es necesario)
    SECRET_KEY: str = "un-secreto-muy-fuerte-y-largo"
    ALGORITHM: str = "HS256"
    
    # Configuración de reintentos
    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 60  # segundos
    
    # Límites
    MAX_RECIPIENTS: int = 50
    EMAIL_TIMEOUT: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Instancia global de configuración
settings = Settings()
