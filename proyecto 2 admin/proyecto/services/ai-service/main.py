import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlmodel import Session, SQLModel, create_engine, select

from config import settings
from db_models import ChatSession, ChatMessage, ChatMetrics, User
from chatbot_service import ChatBotService

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# =============================================================================
# CONFIGURACIÓN DE BASE DE DATOS
# =============================================================================

engine = create_engine(settings.DATABASE_URL, echo=False)
chatbot_service = ChatBotService()

def create_db_and_tables():
    """Crea las tablas de la base de datos"""
    SQLModel.metadata.create_all(engine)
    logger.info("Tablas de base de datos creadas/verificadas")

def get_session():
    """Generador de sesión de base de datos"""
    with Session(engine) as session:
        yield session

# =============================================================================
# AUTENTICACIÓN
# =============================================================================

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_token(token: str = Depends(oauth2_scheme)) -> dict:
    """Verifica y decodifica un token JWT"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("user_id")
        username: str = payload.get("sub")
        email: str = payload.get("email")
        nombre: str = payload.get("nombre")
        
        if user_id is None or username is None:
            raise credentials_exception
            
        return {
            "user_id": user_id, 
            "username": username,
            "email": email,
            "nombre": nombre
        }
    except JWTError:
        raise credentials_exception

# =============================================================================
# MODELOS DE DATOS (Pydantic)
# =============================================================================

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    context: Optional[dict] = None  # Contexto adicional del usuario
    force_new_session: Optional[bool] = False  # Forzar creación de nueva conversación

class ChatResponse(BaseModel):
    response: str
    session_id: str
    tokens_used: Optional[int] = None
    response_time_ms: Optional[int] = None
    error: Optional[str] = None

class SessionHistoryResponse(BaseModel):
    session_id: str
    messages: list[dict]

class MetricsResponse(BaseModel):
    total_conversations: int
    total_messages: int
    total_tokens: int
    avg_response_time_ms: float

# =============================================================================
# CICLO DE VIDA DE LA APLICACIÓN
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    logger.info("🤖 Iniciando servicio de ChatBot IA...")
    create_db_and_tables()
    logger.info("✅ Servicio de ChatBot IA iniciado correctamente")
    yield
    logger.info("🛑 Cerrando servicio de ChatBot IA...")

# =============================================================================
# APLICACIÓN FASTAPI
# =============================================================================

# FastAPI sin middlewares - Nginx maneja CORS y routing
app = FastAPI(
    title="ChatBot IA - Servicio de Asistencia Virtual",
    description="Servicio de chatbot inteligente - CORS manejado por Nginx Gateway",
    version="1.0.0",
    lifespan=lifespan
)

# NOTA: CORS removido - Nginx API Gateway maneja los headers CORS

# =============================================================================
# ENDPOINTS DEL CHATBOT
# =============================================================================

@app.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    user_data: dict = Depends(verify_token),
    db: Session = Depends(get_session)
):
    """
    Endpoint principal para interactuar con el chatbot
    
    - **message**: Mensaje del usuario
    - **session_id**: ID de sesión (opcional, se crea uno nuevo si no se proporciona)
    - **context**: Contexto adicional del usuario (página actual, acción que intenta realizar, etc.)
    - **force_new_session**: Si es True, crea una nueva conversación (botón "Nueva conversación")
    """
    try:
        user_id = user_data["user_id"]
        email = user_data.get("email")
        nombre = user_data.get("nombre")
        
        # Obtener o crear sesión (creará el usuario automáticamente si no existe)
        session = chatbot_service.get_or_create_session(
            db, 
            user_id, 
            request.session_id,
            email,
            nombre,
            force_new=request.force_new_session
        )
        
        # Generar respuesta
        response = await chatbot_service.generate_response(
            db,
            session,
            request.message,
            request.context
        )
        
        return ChatResponse(**response)
        
    except Exception as e:
        logger.error(f"Error en endpoint /chat: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando la consulta: {str(e)}"
        )

@app.post("/chat/public", response_model=ChatResponse)
async def public_chat(
    request: ChatRequest,
    db: Session = Depends(get_session)
):
    """
    Endpoint público para interactuar con el chatbot sin autenticación
    
    - **message**: Mensaje del usuario
    - **session_id**: ID de sesión (opcional, se crea uno nuevo si no se proporciona)
    - **context**: Contexto adicional del usuario
    """
    try:
        # Usar user_id = null para sesiones anónimas
        user_id = None
        
        # Obtener o crear sesión anónima
        session = chatbot_service.get_or_create_anonymous_session(
            db, 
            request.session_id
        )
        
        # Generar respuesta
        response = await chatbot_service.generate_response(
            db,
            session,
            request.message,
            request.context,
            is_anonymous=True
        )
        
        return ChatResponse(**response)
        
    except Exception as e:
        logger.error(f"Error en endpoint /chat/public: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"El servicio de IA no está disponible en este momento. Por favor, intenta más tarde o contacta al administrador."
        )

@app.get("/sessions", response_model=list)
def get_history(
    session_id: str,
    user_data: dict = Depends(verify_token),
    db: Session = Depends(get_session)
):
    """
    Obtiene el historial completo de una sesión de chat
    """
    try:
        # Verificar que la sesión pertenece al usuario
        statement = select(ChatSession).where(
            ChatSession.session_id == session_id,
            ChatSession.user_id == user_data["user_id"]
        )
        session = db.exec(statement).first()
        
        if not session:
            raise HTTPException(
                status_code=404,
                detail="Sesión no encontrada"
            )
        
        messages = chatbot_service.get_session_history(db, session_id)
        
        return SessionHistoryResponse(
            session_id=session_id,
            messages=messages
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo historial: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo historial: {str(e)}"
        )

@app.delete("/chat/session/{session_id}")
def clear_session(
    session_id: str,
    user_data: dict = Depends(verify_token),
    db: Session = Depends(get_session)
):
    """
    Cierra/limpia una sesión de chat
    """
    try:
        success = chatbot_service.clear_session(db, session_id, user_data["user_id"])
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail="Sesión no encontrada"
            )
        
        return {"message": "Sesión cerrada exitosamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cerrando sesión: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error cerrando sesión: {str(e)}"
        )

@app.get("/chat/metrics", response_model=MetricsResponse)
def get_metrics(
    user_data: dict = Depends(verify_token),
    db: Session = Depends(get_session)
):
    """
    Obtiene métricas de uso del chatbot para el usuario actual
    """
    try:
        metrics = chatbot_service.get_user_metrics(db, user_data["user_id"])
        return MetricsResponse(**metrics)
        
    except Exception as e:
        logger.error(f"Error obteniendo métricas: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo métricas: {str(e)}"
        )

@app.get("/chat/conversations")
def get_user_conversations(
    user_data: dict = Depends(verify_token),
    db: Session = Depends(get_session)
):
    """
    Obtiene todas las conversaciones del usuario con preview
    Similar al historial de ChatGPT - muestra lista de conversaciones previas
    """
    try:
        conversations = chatbot_service.get_user_conversations(db, user_data["user_id"])
        return {
            "conversations": conversations
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo conversaciones: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo conversaciones: {str(e)}"
        )

@app.get("/chat/sessions")
def get_user_sessions(
    user_data: dict = Depends(verify_token),
    db: Session = Depends(get_session)
):
    """
    Obtiene todas las sesiones activas del usuario
    (Mantener por compatibilidad - deprecado, usar /chat/conversations)
    """
    try:
        statement = select(ChatSession).where(
            ChatSession.user_id == user_data["user_id"],
            ChatSession.is_active.is_(True)
        ).order_by(ChatSession.updated_at.desc())
        
        sessions = db.exec(statement).all()
        
        return {
            "sessions": [
                {
                    "session_id": s.session_id,
                    "created_at": s.created_at.isoformat(),
                    "updated_at": s.updated_at.isoformat(),
                    "is_active": s.is_active
                }
                for s in sessions
            ]
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo sesiones: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo sesiones: {str(e)}"
        )

# =============================================================================
# ENDPOINTS DE SALUD Y ESTADO
# =============================================================================

@app.get("/health")
def health_check():
    """Endpoint de salud para Docker"""
    return {
        "status": "ok",
        "service": "chatbot-ai",
        "version": "1.0.0"
    }

@app.get("/")
def root():
    """Endpoint raíz con información del servicio"""
    return {
        "service": "ChatBot IA - Asistencia Virtual",
        "version": "1.0.0",
        "description": "Servicio de chatbot inteligente para soporte de usuarios",
        "endpoints": {
            "chat": "POST /chat",
            "history": "GET /chat/history/{session_id}",
            "clear_session": "DELETE /chat/session/{session_id}",
            "metrics": "GET /chat/metrics",
            "sessions": "GET /chat/sessions",
            "health": "GET /health"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=True
    )
