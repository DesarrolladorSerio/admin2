import os
from typing import Optional

from pydantic import BaseModel


class Settings(BaseModel):
    """Configuración del servicio de notificaciones"""
    
    # Aplicación
    APP_NAME: str = "Servicio de Notificaciones"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # SMTP Email Configuration
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM_EMAIL: str = os.getenv("SMTP_FROM_EMAIL", "")
    SMTP_FROM_NAME: str = os.getenv("SMTP_FROM_NAME", "Sistema de Reservas")
    SMTP_TLS: bool = os.getenv("SMTP_TLS", "True").lower() == "true"
    SMTP_SSL: bool = os.getenv("SMTP_SSL", "False").lower() == "true"
    
    # Redis/Queue Configuration
    REDIS_HOST: str = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD")
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0")
    
    # URLs de otros servicios
    AUTH_SERVICE_URL: str = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8000")
    RESERVATIONS_SERVICE_URL: str = os.getenv("RESERVATIONS_SERVICE_URL", "http://reservations-service:8000")
    DOCUMENTS_SERVICE_URL: str = os.getenv("DOCUMENTS_SERVICE_URL", "http://documents-service:8003")
    
    # JWT Configuration (para validar tokens si es necesario)
    SECRET_KEY: str = os.getenv("SECRET_KEY", "un-secreto-muy-fuerte-y-largo")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    
    # Configuración de reintentos
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    RETRY_DELAY: int = int(os.getenv("RETRY_DELAY", "60"))  # segundos
    
    # Límites
    MAX_RECIPIENTS: int = int(os.getenv("MAX_RECIPIENTS", "50"))
    EMAIL_TIMEOUT: int = int(os.getenv("EMAIL_TIMEOUT", "30"))


# Instancia global de configuración
settings = Settings()
