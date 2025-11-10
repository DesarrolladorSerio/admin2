import json
import logging
import time
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

import ollama
import redis
from sqlmodel import Session, select

from config import settings
from db_models import ChatSession, ChatMessage, ChatMetrics, User
from knowledge_base import get_knowledge_context, search_knowledge

logger = logging.getLogger(__name__)

class ChatBotService:
    """Servicio principal del ChatBot con Ollama (100% GRATUITO)"""
    
    def __init__(self):
        self.ollama_client = ollama.Client(host=settings.OLLAMA_BASE_URL)
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True
        )
        self.system_context = get_knowledge_context()
    
    def get_or_create_user(self, db: Session, user_id: int, email: str = None, nombre: str = None) -> User:
        """
        Obtiene un usuario existente o lo crea si no existe
        
        Args:
            db: Sesión de base de datos
            user_id: ID del usuario del sistema de autenticación
            email: Email del usuario (opcional, se usará si se crea el usuario)
            nombre: Nombre del usuario (opcional, se usará si se crea el usuario)
        
        Returns:
            Usuario existente o recién creado
        """
        # Buscar usuario existente
        statement = select(User).where(User.id == user_id)
        user = db.exec(statement).first()
        
        if user:
            logger.debug(f"Usuario encontrado en BD del chatbot: {user_id}")
            return user
        
        # Crear nuevo usuario si no existe
        new_user = User(
            id=user_id,
            email=email or f"user_{user_id}@system.local",
            nombre=nombre or f"Usuario {user_id}"
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"✅ Nuevo usuario creado en BD del chatbot: {user_id} ({new_user.email})")
        return new_user
    
    def create_session(self, db: Session, user_id: int, email: str = None, nombre: str = None) -> ChatSession:
        """
        Crea una nueva sesión de chat para el usuario
        Si el usuario no existe en la BD del chatbot, lo crea automáticamente
        """
        # Asegurar que el usuario existe en la BD del chatbot
        self.get_or_create_user(db, user_id, email, nombre)
        
        session_id = str(uuid.uuid4())
        
        chat_session = ChatSession(
            user_id=user_id,
            session_id=session_id,
            is_active=True
        )
        
        db.add(chat_session)
        db.commit()
        db.refresh(chat_session)
        
        logger.info(f"Nueva sesión de chat creada: {session_id} para usuario {user_id}")
        return chat_session
    
    def create_anonymous_session(self, db: Session) -> ChatSession:
        """Crea una nueva sesión de chat anónima (sin user_id)"""
        session_id = str(uuid.uuid4())
        
        chat_session = ChatSession(
            user_id=None,  # Sesión anónima
            session_id=session_id,
            is_active=True
        )
        
        db.add(chat_session)
        db.commit()
        db.refresh(chat_session)
        
        logger.info(f"Nueva sesión de chat anónima creada: {session_id}")
        return chat_session
    
    def get_or_create_anonymous_session(self, db: Session, session_id: Optional[str] = None) -> ChatSession:
        """Obtiene una sesión anónima existente o crea una nueva"""
        if session_id:
            # Buscar sesión existente anónima
            statement = select(ChatSession).where(
                ChatSession.session_id == session_id,
                ChatSession.user_id.is_(None),  # Sesión anónima
                ChatSession.is_active.is_(True)
            )
            session = db.exec(statement).first()
            
            if session:
                logger.info(f"Sesión anónima encontrada: {session_id}")
                return session
        
        # Crear nueva sesión anónima
        return self.create_anonymous_session(db)
    
    def get_or_create_session(self, db: Session, user_id: int, session_id: Optional[str] = None, email: str = None, nombre: str = None, force_new: bool = False) -> ChatSession:
        """
        Obtiene una sesión existente o crea una nueva
        Si el usuario no existe, lo crea automáticamente
        
        Args:
            force_new: Si es True, siempre crea una nueva sesión (para botón "Nueva conversación")
        """
        # Si se solicita explícitamente una nueva sesión, crearla directamente
        if force_new:
            logger.info(f"Creando nueva sesión forzada para usuario {user_id}")
            return self.create_session(db, user_id, email, nombre)
        
        # Si el cliente provee un session_id, intentar recuperarla (caso ideal)
        if session_id:
            statement = select(ChatSession).where(
                ChatSession.session_id == session_id,
                ChatSession.user_id == user_id
            )
            session = db.exec(statement).first()
            if session:
                return session

        # Si no se entrega session_id, intentar reutilizar una sesión ACTIVA del usuario
        statement_active = select(ChatSession).where(
            ChatSession.user_id == user_id,
            ChatSession.is_active.is_(True)
        ).order_by(ChatSession.updated_at.desc())
        active_session = db.exec(statement_active).first()
        if active_session:
            logger.debug(f"Reusando sesión activa para usuario {user_id}: {active_session.session_id}")
            return active_session

        # Si no hay sesiones activas, intentar recuperar la última sesión (incluso si fue cerrada)
        # Esto evita perder la conversación al recargar (F5) cuando el frontend no envía session_id.
        statement_last = select(ChatSession).where(
            ChatSession.user_id == user_id
        ).order_by(ChatSession.updated_at.desc())
        last_session = db.exec(statement_last).first()
        if last_session:
            logger.debug(f"Reusando última sesión para usuario {user_id}: {last_session.session_id}")
            return last_session

        # Si no existe ninguna sesión, crear una nueva
        return self.create_session(db, user_id, email, nombre)
    
    def get_conversation_history(self, db: Session, session_id: str, limit: int = None) -> List[ChatMessage]:
        """Obtiene el historial de conversación de una sesión"""
        if limit is None:
            limit = settings.MAX_CONVERSATION_HISTORY
        
        # Primero, obtener la sesión por UUID para conseguir el ID numérico
        session_statement = select(ChatSession).where(ChatSession.session_id == session_id)
        session = db.exec(session_statement).first()
        
        if not session:
            return []  # Si no existe la sesión, retornar lista vacía
        
        # Ahora buscar mensajes usando el ID numérico de la sesión
        statement = select(ChatMessage).where(
            ChatMessage.session_id == session.id  # Usar el ID numérico, no el UUID
        ).order_by(ChatMessage.timestamp.desc()).limit(limit)
        
        messages = db.exec(statement).all()
        return list(reversed(messages))  # Ordenar cronológicamente
    
    def _build_conversation_context(self, db: Session, session: ChatSession, user_query: str) -> List[Dict[str, str]]:
        """Construye el contexto de la conversación para Ollama"""
        messages = [
            {"role": "system", "content": self.system_context}
        ]
        
        # Agregar historial reciente
        history = self.get_conversation_history(db, session.session_id, limit=8)
        for msg in history:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Agregar conocimiento específico relevante
        relevant_knowledge = search_knowledge(user_query)
        if relevant_knowledge:
            knowledge_text = "\n\nInformación adicional relevante:\n"
            knowledge_text += json.dumps(relevant_knowledge, indent=2, ensure_ascii=False)
            messages[0]["content"] += knowledge_text
        
        # Agregar consulta actual
        messages.append({
            "role": "user",
            "content": user_query
        })
        
        return messages
    
    async def generate_response(
        self, 
        db: Session, 
        session: ChatSession, 
        user_message: str,
        user_context: Optional[Dict[str, Any]] = None,
        is_anonymous: bool = False
    ) -> Dict[str, Any]:
        """Genera una respuesta usando Ollama (100% GRATUITO - Sin costos API)"""
        start_time = time.time()
        
        try:
            # Agregar contexto del usuario si está disponible
            enhanced_message = user_message
            if user_context:
                context_info = f"\n[Contexto del usuario: {json.dumps(user_context, ensure_ascii=False)}]"
                enhanced_message += context_info
            
            # Guardar mensaje del usuario
            user_msg = ChatMessage(
                session_id=session.id,
                role="user",
                content=user_message
            )
            db.add(user_msg)
            db.commit()
            
            # Construir contexto de conversación
            messages = self._build_conversation_context(db, session, enhanced_message)
            
            # Llamada a Ollama (local, sin costos)
            response = self.ollama_client.chat(
                model=settings.OLLAMA_MODEL,
                messages=messages,
                options={
                    'temperature': 0.7,
                    'num_predict': 500,  # Equivalente a max_tokens
                    'num_ctx': 2048,  # Contexto ajustado para tinyllama (evita warning)
                }
            )
            
            # Extraer respuesta
            assistant_message = response['message']['content']
            
            # Ollama no retorna tokens exactos, estimamos basado en contenido
            tokens_used = len(assistant_message.split()) + len(user_message.split())
            
            # Calcular tiempo de respuesta
            response_time_ms = int((time.time() - start_time) * 1000)
            
            # Guardar respuesta del asistente
            assistant_msg = ChatMessage(
                session_id=session.id,
                role="assistant",
                content=assistant_message,
                tokens_used=tokens_used,
                response_time_ms=response_time_ms
            )
            db.add(assistant_msg)
            
            # Actualizar sesión
            session.updated_at = datetime.utcnow()
            db.add(session)
            db.commit()
            
            # Actualizar métricas
            self._update_metrics(db, session, tokens_used, response_time_ms)
            
            logger.info(f"Respuesta generada en {response_time_ms}ms, ~{tokens_used} tokens")
            
            return {
                "response": assistant_message,
                "session_id": session.session_id,
                "tokens_used": tokens_used,
                "response_time_ms": response_time_ms
            }
            
        except Exception as e:
            logger.error(f"Error en generate_response con Ollama: {str(e)}")
            return {
                "response": "Lo siento, ocurrió un error al procesar tu consulta. Por favor intenta nuevamente o contacta con soporte técnico.",
                "session_id": session.session_id,
                "error": "ollama_error"
            }
    
    def _update_metrics(self, db: Session, session: ChatSession, tokens: int, response_time: int):
        """Actualiza las métricas de uso del chatbot"""
        try:
            # Buscar métricas del día actual
            today = datetime.utcnow().date()
            statement = select(ChatMetrics).where(
                ChatMetrics.session_id == session.id,
                ChatMetrics.date >= datetime.combine(today, datetime.min.time())
            )
            metrics = db.exec(statement).first()
            
            if metrics:
                # Actualizar métricas existentes
                metrics.total_messages += 1
                metrics.total_tokens += tokens
                # Calcular promedio móvil
                total_time = metrics.avg_response_time_ms * (metrics.total_messages - 1) + response_time
                metrics.avg_response_time_ms = total_time / metrics.total_messages
            else:
                # Crear nuevas métricas
                metrics = ChatMetrics(
                    session_id=session.id,
                    user_id=session.user_id,
                    total_messages=1,
                    total_tokens=tokens,
                    avg_response_time_ms=float(response_time)
                )
            
            db.add(metrics)
            db.commit()
        except Exception as e:
            logger.error(f"Error actualizando métricas: {str(e)}")
    
    def get_session_history(self, db: Session, session_id: str) -> List[Dict[str, Any]]:
        """Obtiene el historial completo de una sesión"""
        statement = select(ChatSession).where(ChatSession.session_id == session_id)
        session = db.exec(statement).first()
        
        if not session:
            return []
        
        messages = self.get_conversation_history(db, session.session_id, limit=100)
        
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "tokens_used": msg.tokens_used,
                "response_time_ms": msg.response_time_ms
            }
            for msg in messages
        ]
    
    def get_user_conversations(self, db: Session, user_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene todas las conversaciones del usuario con información resumida
        Similar al historial de ChatGPT
        """
        # Obtener todas las sesiones del usuario, ordenadas por última actualización
        statement = select(ChatSession).where(
            ChatSession.user_id == user_id
        ).order_by(ChatSession.updated_at.desc())
        
        sessions = db.exec(statement).all()
        
        conversations = []
        for session in sessions:
            # Obtener el primer mensaje del usuario para el preview
            first_message_statement = select(ChatMessage).where(
                ChatMessage.session_id == session.id,
                ChatMessage.role == "user"
            ).order_by(ChatMessage.timestamp.asc()).limit(1)
            
            first_msg = db.exec(first_message_statement).first()
            
            # Contar mensajes totales
            count_statement = select(ChatMessage).where(
                ChatMessage.session_id == session.id
            )
            message_count = len(db.exec(count_statement).all())
            
            # Crear preview del contenido (primeros 50 caracteres del primer mensaje)
            preview = "Nueva conversación"
            if first_msg:
                preview = first_msg.content[:50] + "..." if len(first_msg.content) > 50 else first_msg.content
            
            conversations.append({
                "session_id": session.session_id,
                "created_at": session.created_at.isoformat(),
                "updated_at": session.updated_at.isoformat(),
                "is_active": session.is_active,
                "message_count": message_count,
                "preview": preview
            })
        
        return conversations
    
    def clear_session(self, db: Session, session_id: str, user_id: int) -> bool:
        """
        Cierra una sesión de chat y ELIMINA todo el historial de mensajes.
        Usado cuando el usuario presiona el botón de cerrar sesión en la UI.
        """
        statement = select(ChatSession).where(
            ChatSession.session_id == session_id,
            ChatSession.user_id == user_id
        )
        session = db.exec(statement).first()
        
        if session:
            # Eliminar todos los mensajes de esta sesión
            delete_messages_statement = select(ChatMessage).where(
                ChatMessage.session_id == session.id
            )
            messages = db.exec(delete_messages_statement).all()
            for msg in messages:
                db.delete(msg)
            
            # Marcar sesión como inactiva (o podrías eliminarla también)
            session.is_active = False
            db.add(session)
            db.commit()
            
            logger.info(f"Sesión {session_id} cerrada y {len(messages)} mensajes eliminados")
            return True
        
        return False
    
    def get_user_metrics(self, db: Session, user_id: int) -> Dict[str, Any]:
        """Obtiene métricas agregadas del usuario"""
        statement = select(ChatMetrics).where(ChatMetrics.user_id == user_id)
        all_metrics = db.exec(statement).all()
        
        if not all_metrics:
            return {
                "total_conversations": 0,
                "total_messages": 0,
                "total_tokens": 0,
                "avg_response_time_ms": 0
            }
        
        total_messages = sum(m.total_messages for m in all_metrics)
        total_tokens = sum(m.total_tokens for m in all_metrics)
        
        avg_response_time = 0
        if all_metrics:
            avg_response_time = sum(m.avg_response_time_ms for m in all_metrics) / len(all_metrics)
        
        return {
            "total_conversations": len(all_metrics),
            "total_messages": total_messages,
            "total_tokens": total_tokens,
            "avg_response_time_ms": round(avg_response_time, 2)
        }
