import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional, Dict, Any
from jinja2 import Environment, FileSystemLoader, select_autoescape
import logging
from pathlib import Path
from config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Servicio para envío de emails con templates HTML"""
    
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.SMTP_FROM_EMAIL
        self.from_name = settings.SMTP_FROM_NAME
        
        # Configurar Jinja2 para templates
        template_dir = Path(__file__).parent / "templates"
        template_dir.mkdir(exist_ok=True)
        
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(['html', 'xml'])
        )
    
    async def send_email(
        self,
        to_emails: List[str],
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None
    ) -> bool:
        """
        Enviar email con soporte para HTML, texto plano y adjuntos
        
        Args:
            to_emails: Lista de destinatarios
            subject: Asunto del email
            html_body: Cuerpo HTML del email
            text_body: Cuerpo en texto plano (opcional)
            attachments: Lista de adjuntos (opcional)
            cc: Lista de destinatarios en copia
            bcc: Lista de destinatarios en copia oculta
        
        Returns:
            bool: True si el email se envió correctamente
        """
        try:
            # Validar límite de destinatarios
            total_recipients = len(to_emails) + len(cc or []) + len(bcc or [])
            if total_recipients > settings.MAX_RECIPIENTS:
                logger.error(f"Demasiados destinatarios: {total_recipients}")
                return False
            
            # Crear mensaje
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = ", ".join(to_emails)
            
            if cc:
                message["Cc"] = ", ".join(cc)
            if bcc:
                message["Bcc"] = ", ".join(bcc)
            
            # Agregar cuerpo en texto plano
            if text_body:
                text_part = MIMEText(text_body, "plain", "utf-8")
                message.attach(text_part)
            
            # Agregar cuerpo HTML
            html_part = MIMEText(html_body, "html", "utf-8")
            message.attach(html_part)
            
            # Agregar adjuntos si existen
            if attachments:
                for attachment in attachments:
                    self._attach_file(message, attachment)
            
            # Enviar email
            await self._send_smtp(message, to_emails + (cc or []) + (bcc or []))
            
            logger.info(f"Email enviado exitosamente a {len(to_emails)} destinatarios")
            return True
            
        except Exception as e:
            logger.error(f"Error al enviar email: {str(e)}", exc_info=True)
            return False
    
    def _attach_file(self, message: MIMEMultipart, attachment: Dict[str, Any]):
        """Adjuntar archivo al mensaje"""
        try:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment["content"])
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {attachment['filename']}"
            )
            message.attach(part)
        except Exception as e:
            logger.error(f"Error al adjuntar archivo: {str(e)}")
    
    async def _send_smtp(self, message: MIMEMultipart, recipients: List[str]):
        """Enviar email via SMTP"""
        smtp_params = {
            "hostname": self.smtp_host,
            "port": self.smtp_port,
            "timeout": settings.EMAIL_TIMEOUT,
        }
        
        if settings.SMTP_TLS:
            # Para STARTTLS (puerto 587 de Gmail)
            smtp_params["use_tls"] = False
            smtp_params["start_tls"] = True
        elif settings.SMTP_SSL:
            # Para SSL directo (puerto 465)
            smtp_params["use_tls"] = True
            smtp_params["start_tls"] = False
        
        async with aiosmtplib.SMTP(**smtp_params) as smtp:
            if self.smtp_user and self.smtp_password:
                await smtp.login(self.smtp_user, self.smtp_password)
            
            await smtp.send_message(message, recipients=recipients)
    
    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Renderizar template HTML con contexto
        
        Args:
            template_name: Nombre del archivo de template
            context: Diccionario con variables para el template
        
        Returns:
            str: HTML renderizado
        """
        try:
            template = self.jinja_env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            logger.error(f"Error al renderizar template {template_name}: {str(e)}")
            return ""
    
    async def send_reservation_confirmation(
        self,
        user_email: str,
        user_name: str,
        reservation_data: Dict[str, Any]
    ) -> bool:
        """Enviar email de confirmación de reserva"""
        try:
            context = {
                "user_name": user_name,
                "reservation_id": reservation_data.get("id"),
                "date": reservation_data.get("date"),
                "time": reservation_data.get("time"),
                "service": reservation_data.get("service"),
                "location": reservation_data.get("location"),
            }
            
            html_body = self.render_template("reservation_confirmation.html", context)
            
            subject = f"Confirmación de Reserva #{reservation_data.get('id')}"
            
            return await self.send_email(
                to_emails=[user_email],
                subject=subject,
                html_body=html_body
            )
        except Exception as e:
            logger.error(f"Error al enviar confirmación de reserva: {str(e)}")
            return False
    
    async def send_reservation_reminder(
        self,
        user_email: str,
        user_name: str,
        reservation_data: Dict[str, Any]
    ) -> bool:
        """Enviar recordatorio de reserva"""
        try:
            context = {
                "user_name": user_name,
                "reservation_id": reservation_data.get("id"),
                "date": reservation_data.get("date"),
                "time": reservation_data.get("time"),
                "service": reservation_data.get("service"),
                "location": reservation_data.get("location"),
            }
            
            html_body = self.render_template("reservation_reminder.html", context)
            
            subject = f"Recordatorio: Reserva #{reservation_data.get('id')} mañana"
            
            return await self.send_email(
                to_emails=[user_email],
                subject=subject,
                html_body=html_body
            )
        except Exception as e:
            logger.error(f"Error al enviar recordatorio: {str(e)}")
            return False
    
    async def send_reservation_cancellation(
        self,
        user_email: str,
        user_name: str,
        reservation_data: Dict[str, Any]
    ) -> bool:
        """Enviar notificación de cancelación de reserva"""
        try:
            context = {
                "user_name": user_name,
                "reservation_id": reservation_data.get("id"),
                "date": reservation_data.get("date"),
                "time": reservation_data.get("time"),
                "service": reservation_data.get("service"),
            }
            
            html_body = self.render_template("reservation_cancellation.html", context)
            
            subject = f"Cancelación de Reserva #{reservation_data.get('id')}"
            
            return await self.send_email(
                to_emails=[user_email],
                subject=subject,
                html_body=html_body
            )
        except Exception as e:
            logger.error(f"Error al enviar cancelación: {str(e)}")
            return False
    
    async def send_document_notification(
        self,
        user_email: str,
        user_name: str,
        document_data: Dict[str, Any],
        notification_type: str = "uploaded"
    ) -> bool:
        """Enviar notificación sobre documentos"""
        try:
            context = {
                "user_name": user_name,
                "document_name": document_data.get("name"),
                "document_type": document_data.get("type"),
                "notification_type": notification_type,
                "upload_date": document_data.get("upload_date"),
            }
            
            html_body = self.render_template("document_notification.html", context)
            
            subject_map = {
                "uploaded": "Documento subido exitosamente",
                "approved": "Documento aprobado",
                "rejected": "Documento requiere revisión",
            }
            
            subject = subject_map.get(notification_type, "Notificación de documento")
            
            return await self.send_email(
                to_emails=[user_email],
                subject=subject,
                html_body=html_body
            )
        except Exception as e:
            logger.error(f"Error al enviar notificación de documento: {str(e)}")
            return False
    
    async def send_welcome_email(
        self,
        user_email: str,
        user_name: str,
        temp_password: Optional[str] = None
    ) -> bool:
        """Enviar email de bienvenida a nuevo usuario"""
        try:
            context = {
                "user_name": user_name,
                "user_email": user_email,
                "temp_password": temp_password,
            }
            
            html_body = self.render_template("welcome.html", context)
            
            subject = "Bienvenido al Sistema de Reservas"
            
            return await self.send_email(
                to_emails=[user_email],
                subject=subject,
                html_body=html_body
            )
        except Exception as e:
            logger.error(f"Error al enviar email de bienvenida: {str(e)}")
            return False
    
    async def send_password_reset(
        self,
        user_email: str,
        user_name: str,
        reset_token: str,
        reset_url: str
    ) -> bool:
        """Enviar email de recuperación de contraseña"""
        try:
            context = {
                "user_name": user_name,
                "reset_url": f"{reset_url}?token={reset_token}",
                "reset_token": reset_token,
            }
            
            html_body = self.render_template("password_reset.html", context)
            
            subject = "Recuperación de Contraseña"
            
            return await self.send_email(
                to_emails=[user_email],
                subject=subject,
                html_body=html_body
            )
        except Exception as e:
            logger.error(f"Error al enviar recuperación de contraseña: {str(e)}")
            return False


# Instancia global del servicio de email
email_service = EmailService()
