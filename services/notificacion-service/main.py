import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import redis
from config import settings
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr
from tasks import (
    send_batch_emails_task,
    send_document_notification_task,
    send_email_task,
    send_password_reset_task,
    send_reservation_cancellation_task,
    send_reservation_confirmation_task,
    send_reservation_reminder_task,
    send_welcome_email_task,
)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI sin middlewares - Nginx maneja CORS y routing
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Servicio de notificaciones - CORS manejado por Nginx Gateway"
)

# NOTA: CORS removido - Nginx API Gateway maneja los headers CORS

# Conexión a Redis
try:
    redis_client = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        password=settings.REDIS_PASSWORD,
        decode_responses=True
    )
except Exception as e:
    logger.error(f"Error al conectar con Redis: {str(e)}")
    redis_client = None


# ============================================
# Modelos Pydantic
# ============================================

class EmailRequest(BaseModel):
    to_emails: List[EmailStr]
    subject: str
    html_body: str
    text_body: Optional[str] = None
    cc: Optional[List[EmailStr]] = None
    bcc: Optional[List[EmailStr]] = None


class ReservationNotification(BaseModel):
    user_email: EmailStr
    user_name: str
    reservation_data: Dict[str, Any]


class DocumentNotification(BaseModel):
    user_email: EmailStr
    user_name: str
    document_data: Dict[str, Any]
    notification_type: str = "uploaded"  # uploaded, approved, rejected


class WelcomeEmail(BaseModel):
    user_email: EmailStr
    user_name: str
    temp_password: Optional[str] = None


class PasswordResetEmail(BaseModel):
    user_email: EmailStr
    user_name: str
    reset_token: str
    reset_url: str


class BatchEmailRequest(BaseModel):
    emails: List[EmailRequest]


class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str


# ============================================
# Endpoints de Health Check
# ============================================

@app.get("/health")
async def health_check():
    """Verificar estado del servicio"""
    health_status = {
        "service": "notifications",
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "redis": "disconnected",
        "celery": "unknown"
    }
    
    # Verificar Redis
    if redis_client:
        try:
            redis_client.ping()
            health_status["redis"] = "connected"
        except Exception as e:
            health_status["redis"] = f"error: {str(e)}"
            health_status["status"] = "degraded"
    
    return health_status


@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


# ============================================
# Endpoints de Notificaciones
# ============================================

@app.post("/api/notifications/email", response_model=TaskResponse)
async def send_email(email_data: EmailRequest):
    """
    Enviar email genérico (encola en Celery)
    """
    try:
        task = send_email_task.delay(
            to_emails=email_data.to_emails,
            subject=email_data.subject,
            html_body=email_data.html_body,
            text_body=email_data.text_body,
            cc=email_data.cc,
            bcc=email_data.bcc
        )
        
        logger.info(f"Email encolado con task_id: {task.id}")
        
        return TaskResponse(
            task_id=task.id,
            status="queued",
            message=f"Email encolado para {len(email_data.to_emails)} destinatarios"
        )
    
    except Exception as e:
        logger.error(f"Error al encolar email: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al encolar email: {str(e)}"
        )


@app.post("/api/notifications/reservation/confirmation", response_model=TaskResponse)
async def send_reservation_confirmation(notification: ReservationNotification):
    """
    Enviar confirmación de reserva
    """
    try:
        task = send_reservation_confirmation_task.delay(
            user_email=notification.user_email,
            user_name=notification.user_name,
            reservation_data=notification.reservation_data
        )
        
        logger.info(f"Confirmación de reserva encolada: {task.id}")
        
        return TaskResponse(
            task_id=task.id,
            status="queued",
            message="Confirmación de reserva encolada"
        )
    
    except Exception as e:
        logger.error(f"Error al encolar confirmación: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al encolar confirmación: {str(e)}"
        )


@app.post("/api/notifications/reservation/reminder", response_model=TaskResponse)
async def send_reservation_reminder(notification: ReservationNotification):
    """
    Enviar recordatorio de reserva
    """
    try:
        task = send_reservation_reminder_task.delay(
            user_email=notification.user_email,
            user_name=notification.user_name,
            reservation_data=notification.reservation_data
        )
        
        logger.info(f"Recordatorio encolado: {task.id}")
        
        return TaskResponse(
            task_id=task.id,
            status="queued",
            message="Recordatorio encolado"
        )
    
    except Exception as e:
        logger.error(f"Error al encolar recordatorio: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al encolar recordatorio: {str(e)}"
        )


@app.post("/api/notifications/reservation/cancellation", response_model=TaskResponse)
async def send_reservation_cancellation(notification: ReservationNotification):
    """
    Enviar notificación de cancelación de reserva
    """
    try:
        task = send_reservation_cancellation_task.delay(
            user_email=notification.user_email,
            user_name=notification.user_name,
            reservation_data=notification.reservation_data
        )
        
        logger.info(f"Cancelación encolada: {task.id}")
        
        return TaskResponse(
            task_id=task.id,
            status="queued",
            message="Notificación de cancelación encolada"
        )
    
    except Exception as e:
        logger.error(f"Error al encolar cancelación: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al encolar cancelación: {str(e)}"
        )


@app.post("/api/notifications/document", response_model=TaskResponse)
async def send_document_notification(notification: DocumentNotification):
    """
    Enviar notificación sobre documento
    """
    try:
        task = send_document_notification_task.delay(
            user_email=notification.user_email,
            user_name=notification.user_name,
            document_data=notification.document_data,
            notification_type=notification.notification_type
        )
        
        logger.info(f"Notificación de documento encolada: {task.id}")
        
        return TaskResponse(
            task_id=task.id,
            status="queued",
            message="Notificación de documento encolada"
        )
    
    except Exception as e:
        logger.error(f"Error al encolar notificación: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al encolar notificación: {str(e)}"
        )


@app.post("/api/notifications/welcome", response_model=TaskResponse)
async def send_welcome(email_data: WelcomeEmail):
    """
    Enviar email de bienvenida a nuevo usuario
    """
    try:
        task = send_welcome_email_task.delay(
            user_email=email_data.user_email,
            user_name=email_data.user_name,
            temp_password=email_data.temp_password
        )
        
        logger.info(f"Email de bienvenida encolado: {task.id}")
        
        return TaskResponse(
            task_id=task.id,
            status="queued",
            message="Email de bienvenida encolado"
        )
    
    except Exception as e:
        logger.error(f"Error al encolar bienvenida: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al encolar bienvenida: {str(e)}"
        )


@app.post("/api/notifications/password-reset", response_model=TaskResponse)
async def send_password_reset(email_data: PasswordResetEmail):
    """
    Enviar email de recuperación de contraseña
    """
    try:
        task = send_password_reset_task.delay(
            user_email=email_data.user_email,
            user_name=email_data.user_name,
            reset_token=email_data.reset_token,
            reset_url=email_data.reset_url
        )
        
        logger.info(f"Email de recuperación encolado: {task.id}")
        
        return TaskResponse(
            task_id=task.id,
            status="queued",
            message="Email de recuperación encolado"
        )
    
    except Exception as e:
        logger.error(f"Error al encolar recuperación: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al encolar recuperación: {str(e)}"
        )


@app.post("/api/notifications/batch", response_model=TaskResponse)
async def send_batch_emails(batch_data: BatchEmailRequest):
    """
    Enviar múltiples emails en lote
    """
    try:
        email_list = [email.model_dump() for email in batch_data.emails]
        
        task = send_batch_emails_task.delay(email_list)
        
        logger.info(f"Lote de {len(email_list)} emails encolado: {task.id}")
        
        return TaskResponse(
            task_id=task.id,
            status="queued",
            message=f"Lote de {len(email_list)} emails encolado"
        )
    
    except Exception as e:
        logger.error(f"Error al encolar lote: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al encolar lote: {str(e)}"
        )


# ============================================
# Endpoints de Estado de Tareas
# ============================================

@app.get("/api/notifications/task/{task_id}")
async def get_task_status(task_id: str):
    """
    Consultar estado de una tarea
    """
    try:
        from celery.result import AsyncResult
        from celery_config import celery_app
        
        task_result = AsyncResult(task_id, app=celery_app)
        
        response = {
            "task_id": task_id,
            "status": task_result.state,
            "result": None
        }
        
        if task_result.ready():
            response["result"] = task_result.result
        
        if task_result.failed():
            response["error"] = str(task_result.info)
        
        return response
    
    except Exception as e:
        logger.error(f"Error al consultar tarea: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al consultar tarea: {str(e)}"
        )


@app.get("/api/notifications/stats")
async def get_stats():
    """
    Obtener estadísticas del servicio
    """
    try:
        stats = {
            "service": settings.APP_NAME,
            "redis_connected": False,
            "pending_tasks": 0,
            "timestamp": datetime.now().isoformat()
        }
        
        if redis_client:
            try:
                redis_client.ping()
                stats["redis_connected"] = True
                # Aquí podrías agregar más estadísticas de Redis/Celery
            except Exception as e:
                logger.warning(f"Redis connection error: {e}")
                stats["redis_connected"] = False
        
        return stats
    
    except Exception as e:
        logger.error(f"Error al obtener estadísticas: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estadísticas: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
