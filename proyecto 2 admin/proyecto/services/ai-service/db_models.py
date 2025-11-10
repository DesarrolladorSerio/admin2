from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship

class ChatSession(SQLModel, table=True):
    """Sesión de chat del usuario"""
    __tablename__ = "chat_sessions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="users.id", index=True)
    session_id: str = Field(index=True, unique=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    
    # Relación con mensajes
    messages: list["ChatMessage"] = Relationship(back_populates="session")

class ChatMessage(SQLModel, table=True):
    """Mensaje individual en una conversación"""
    __tablename__ = "chat_messages"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="chat_sessions.id", index=True)
    role: str = Field(max_length=20)  # 'user' o 'assistant'
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    tokens_used: Optional[int] = None
    response_time_ms: Optional[int] = None
    
    # Relación con sesión
    session: ChatSession = Relationship(back_populates="messages")

class ChatMetrics(SQLModel, table=True):
    """Métricas de uso del chatbot"""
    __tablename__ = "chat_metrics"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="chat_sessions.id", index=True)
    user_id: Optional[int] = Field(default=None, index=True)
    date: datetime = Field(default_factory=datetime.utcnow, index=True)
    total_messages: int = Field(default=0)
    total_tokens: int = Field(default=0)
    avg_response_time_ms: float = Field(default=0.0)
    topics_discussed: str = Field(default="")  # JSON string con tópicos
    satisfaction_rating: Optional[int] = None  # 1-5 si el usuario califica

# Tabla simple para usuarios (referencia desde auth-service)
class User(SQLModel, table=True):
    """Referencia simple a usuarios del sistema"""
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    nombre: str
