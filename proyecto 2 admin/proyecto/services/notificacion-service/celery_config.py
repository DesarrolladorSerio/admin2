from celery import Celery
from config import settings

# Crear instancia de Celery
celery_app = Celery(
    "notifications",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["tasks"]
)

# Configuración de Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Santiago",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutos
    task_soft_time_limit=240,  # 4 minutos
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    broker_connection_retry_on_startup=True,
)

# Configuración de reintentos
celery_app.conf.task_default_retry_delay = settings.RETRY_DELAY
celery_app.conf.task_max_retries = settings.MAX_RETRIES
