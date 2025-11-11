import logging
from typing import Any, Dict, List

from celery_config import celery_app
from email_service import email_service

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="tasks.send_email_task")
def send_email_task(
    self,
    to_emails: List[str],
    subject: str,
    html_body: str,
    text_body: str | None = None,
    cc: List[str] | None = None,
    bcc: List[str] | None = None
):
    """
    Tarea asíncrona para enviar email
    """
    try:
        import asyncio
        result = asyncio.run(
            email_service.send_email(
                to_emails=to_emails,
                subject=subject,
                html_body=html_body,
                text_body=text_body,
                cc=cc,
                bcc=bcc
            )
        )
        
        if result:
            logger.info(f"Email enviado exitosamente a {to_emails}")
            return {"status": "success", "recipients": to_emails}
        else:
            logger.error(f"Error al enviar email a {to_emails}")
            raise Exception("Error al enviar email")
            
    except Exception as e:
        logger.error(f"Error en tarea de email: {str(e)}")
        # Reintentar la tarea
        raise self.retry(exc=e, countdown=60)


@celery_app.task(bind=True, name="tasks.send_reservation_confirmation_task")
def send_reservation_confirmation_task(
    self,
    user_email: str,
    user_name: str,
    reservation_data: Dict[str, Any]
):
    """
    Tarea asíncrona para enviar confirmación de reserva
    """
    try:
        import asyncio
        result = asyncio.run(
            email_service.send_reservation_confirmation(
                user_email=user_email,
                user_name=user_name,
                reservation_data=reservation_data
            )
        )
        
        if result:
            logger.info(f"Confirmación de reserva enviada a {user_email}")
            return {"status": "success", "recipient": user_email}
        else:
            raise Exception("Error al enviar confirmación")
            
    except Exception as e:
        logger.error(f"Error en tarea de confirmación: {str(e)}")
        raise self.retry(exc=e, countdown=60)


@celery_app.task(bind=True, name="tasks.send_reservation_reminder_task")
def send_reservation_reminder_task(
    self,
    user_email: str,
    user_name: str,
    reservation_data: Dict[str, Any]
):
    """
    Tarea asíncrona para enviar recordatorio de reserva
    """
    try:
        import asyncio
        result = asyncio.run(
            email_service.send_reservation_reminder(
                user_email=user_email,
                user_name=user_name,
                reservation_data=reservation_data
            )
        )
        
        if result:
            logger.info(f"Recordatorio enviado a {user_email}")
            return {"status": "success", "recipient": user_email}
        else:
            raise Exception("Error al enviar recordatorio")
            
    except Exception as e:
        logger.error(f"Error en tarea de recordatorio: {str(e)}")
        raise self.retry(exc=e, countdown=60)


@celery_app.task(bind=True, name="tasks.send_reservation_cancellation_task")
def send_reservation_cancellation_task(
    self,
    user_email: str,
    user_name: str,
    reservation_data: Dict[str, Any]
):
    """
    Tarea asíncrona para enviar notificación de cancelación
    """
    try:
        import asyncio
        result = asyncio.run(
            email_service.send_reservation_cancellation(
                user_email=user_email,
                user_name=user_name,
                reservation_data=reservation_data
            )
        )
        
        if result:
            logger.info(f"Cancelación notificada a {user_email}")
            return {"status": "success", "recipient": user_email}
        else:
            raise Exception("Error al enviar cancelación")
            
    except Exception as e:
        logger.error(f"Error en tarea de cancelación: {str(e)}")
        raise self.retry(exc=e, countdown=60)


@celery_app.task(bind=True, name="tasks.send_document_notification_task")
def send_document_notification_task(
    self,
    user_email: str,
    user_name: str,
    document_data: Dict[str, Any],
    notification_type: str = "uploaded"
):
    """
    Tarea asíncrona para enviar notificación de documento
    """
    try:
        import asyncio
        result = asyncio.run(
            email_service.send_document_notification(
                user_email=user_email,
                user_name=user_name,
                document_data=document_data,
                notification_type=notification_type
            )
        )
        
        if result:
            logger.info(f"Notificación de documento enviada a {user_email}")
            return {"status": "success", "recipient": user_email}
        else:
            raise Exception("Error al enviar notificación")
            
    except Exception as e:
        logger.error(f"Error en tarea de notificación: {str(e)}")
        raise self.retry(exc=e, countdown=60)


@celery_app.task(bind=True, name="tasks.send_welcome_email_task")
def send_welcome_email_task(
    self,
    user_email: str,
    user_name: str,
    temp_password: str | None = None
):
    """
    Tarea asíncrona para enviar email de bienvenida
    """
    try:
        import asyncio
        result = asyncio.run(
            email_service.send_welcome_email(
                user_email=user_email,
                user_name=user_name,
                temp_password=temp_password
            )
        )
        
        if result:
            logger.info(f"Email de bienvenida enviado a {user_email}")
            return {"status": "success", "recipient": user_email}
        else:
            raise Exception("Error al enviar bienvenida")
            
    except Exception as e:
        logger.error(f"Error en tarea de bienvenida: {str(e)}")
        raise self.retry(exc=e, countdown=60)


@celery_app.task(bind=True, name="tasks.send_password_reset_task")
def send_password_reset_task(
    self,
    user_email: str,
    user_name: str,
    reset_token: str,
    reset_url: str
):
    """
    Tarea asíncrona para enviar email de recuperación de contraseña
    """
    try:
        import asyncio
        result = asyncio.run(
            email_service.send_password_reset(
                user_email=user_email,
                user_name=user_name,
                reset_token=reset_token,
                reset_url=reset_url
            )
        )
        
        if result:
            logger.info(f"Email de recuperación enviado a {user_email}")
            return {"status": "success", "recipient": user_email}
        else:
            raise Exception("Error al enviar recuperación")
            
    except Exception as e:
        logger.error(f"Error en tarea de recuperación: {str(e)}")
        raise self.retry(exc=e, countdown=60)


@celery_app.task(name="tasks.send_batch_emails_task")
def send_batch_emails_task(email_list: List[Dict[str, Any]]):
    """
    Tarea para enviar múltiples emails en lote
    
    Args:
        email_list: Lista de diccionarios con datos de emails
    """
    results = []
    for email_data in email_list:
        try:
            task = send_email_task.delay(
                to_emails=email_data["to_emails"],
                subject=email_data["subject"],
                html_body=email_data["html_body"],
                text_body=email_data.get("text_body"),
                cc=email_data.get("cc"),
                bcc=email_data.get("bcc")
            )
            results.append({"task_id": task.id, "recipient": email_data["to_emails"]})
        except Exception as e:
            logger.error(f"Error al encolar email: {str(e)}")
            results.append({"error": str(e), "recipient": email_data["to_emails"]})
    
    return {"status": "batch_queued", "results": results}
