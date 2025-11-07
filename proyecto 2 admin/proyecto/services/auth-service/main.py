from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from pydantic import BaseModel, EmailStr, constr
from sqlmodel import Session
import httpx
import logging

# Importar funciones de base de datos
from db_auth import (
    create_db_and_tables, 
    get_session, 
    authenticate_user,
    init_default_users,
    get_user_by_username,
    get_user_by_email,
    get_user_by_rut,
    get_user_by_login_identifier,
    create_user,
    User
)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# CONFIGURACIÓN
# =============================================================================

SECRET_KEY = "un-secreto-muy-fuerte-y-largo"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

# Configurar CORS para permitir peticiones desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Permitir todos los orígenes para depuración
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# =============================================================================
# MODELOS DE DATOS (Pydantic)
# =============================================================================
class LoginRequest(BaseModel):
    identifier: str  # Puede ser email o RUT
    password: str
    login_type: str = "email"  # "email" o "rut"

class UserCreate(BaseModel):
    email: EmailStr  # Email válido requerido
    nombre: str      # Nombre completo
    rut: str         # RUT OBLIGATORIO
    password: str    # Contraseña (validación mínimo 8 caracteres se hará en el endpoint)

class UserResponse(BaseModel):
    id: int
    username: str  # Mantener para compatibilidad
    email: str
    nombre: str
    rut: str | None

class Token(BaseModel):
    access_token: str
    token_type: str

# =============================================================================
# FUNCIONES DE AUTENTICACIÓN
# =============================================================================

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Crea un nuevo token de acceso."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str = Depends(oauth2_scheme)):
    """Verifica y decodifica un token JWT."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return username

def get_current_user(
    username: str = Depends(verify_token),
    session: Session = Depends(get_session)
) -> User:
    """Obtiene el usuario actual basado en el token."""
    user = get_user_by_username(session, username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

# =============================================================================
# EVENTOS DE APLICACIÓN
# =============================================================================

@app.on_event("startup")
def on_startup():
    """Inicializa la base de datos al arrancar la aplicación."""
    create_db_and_tables()
    
    # Crear usuarios por defecto
    with next(get_session()) as session:
        init_default_users(session)

# =============================================================================
# FUNCIONES AUXILIARES PARA NOTIFICACIONES
# =============================================================================

async def send_notification(endpoint: str, data: dict):
    """
    Enviar notificación al servicio de notificaciones
    No bloquea si falla, solo registra el error
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                f"http://notifications-service:8004/api/notifications/{endpoint}",
                json=data
            )
            logger.info(f"Notificación enviada: {endpoint} - Status: {response.status_code}")
            return response.json()
    except Exception as e:
        logger.error(f"Error enviando notificación a {endpoint}: {str(e)}")
        return None

# =============================================================================
# ENDPOINTS DE LA API
# =============================================================================

@app.post("/token", response_model=Token)
async def login_for_access_token(
    login_data: LoginRequest,
    session: Session = Depends(get_session)
):
    """Endpoint para el login con JSON. Soporta email y RUT."""
    user = authenticate_user(session, login_data.identifier, login_data.password)
    if not user:
        login_type_msg = "email" if login_data.login_type == "email" else "RUT"
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Incorrect {login_type_msg} or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/register", response_model=Token)
async def register_user(
    user_data: UserCreate,
    session: Session = Depends(get_session)
):
    """Registra un nuevo usuario con email, nombre y opcionalmente RUT."""
    
    # Validar longitud de contraseña
    if len(user_data.password) < 8:
        raise HTTPException(
            status_code=400,
            detail="La contraseña debe tener al menos 8 caracteres"
        )
    
    # Verificar si el email ya existe
    existing_user = get_user_by_email(session, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="El email ya está registrado"
        )
    
    # Verificar si el RUT ya existe (si se proporciona)
    if user_data.rut:
        existing_rut = get_user_by_rut(session, user_data.rut)
        if existing_rut:
            raise HTTPException(
                status_code=400,
                detail="El RUT ya está registrado"
            )
    
    # Crear nuevo usuario
    new_user = create_user(
        session, 
        username=user_data.email,  # usar email como username para compatibilidad
        email=user_data.email,
        nombre=user_data.nombre,
        password=user_data.password,
        rut=user_data.rut
    )
    
    # 📧 Enviar email de bienvenida (asíncrono, no bloquea)
    await send_notification(
        "welcome",
        {
            "user_email": new_user.email,
            "user_name": new_user.nombre,
            "temp_password": None  # No enviamos la contraseña por email
        }
    )
    
    # Crear token automáticamente
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": new_user.email, "user_id": new_user.id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# =============================================================================
# ENDPOINTS DE USUARIOS (para consulta desde otros servicios)
# =============================================================================

@app.get("/users/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Obtiene la información del usuario autenticado actual."""
    return UserResponse(
        id=current_user.id, 
        username=current_user.username,
        email=current_user.email,
        nombre=current_user.nombre,
        rut=current_user.rut
    )

@app.get("/users", response_model=list[UserResponse])
def get_all_users(session: Session = Depends(get_session)):
    """Obtiene todos los usuarios registrados."""
    from sqlmodel import select
    statement = select(User)
    users = session.exec(statement).all()
    return [
        UserResponse(
            id=user.id, 
            username=user.username,
            email=user.email,
            nombre=user.nombre,
            rut=user.rut
        ) for user in users
    ]

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user_by_id(user_id: int, session: Session = Depends(get_session)):
    """Obtiene un usuario específico por ID."""
    from sqlmodel import select
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return UserResponse(
        id=user.id, 
        username=user.username,
        email=user.email,
        nombre=user.nombre,
        rut=user.rut
    )

# =============================================================================
# ENDPOINTS DE RECUPERACIÓN DE CONTRASEÑA
# =============================================================================

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

@app.post("/password-reset/request")
async def request_password_reset(
    reset_data: PasswordResetRequest,
    session: Session = Depends(get_session)
):
    """Solicita un token para restablecer la contraseña."""
    
    # Buscar usuario por email
    user = get_user_by_email(session, reset_data.email)
    
    # Por seguridad, siempre devolver éxito aunque el email no exista
    # Esto evita que se puedan enumerar emails válidos
    if not user:
        logger.warning(f"Intento de recuperación para email inexistente: {reset_data.email}")
        return {"message": "Si el email existe, se enviará un enlace de recuperación"}
    
    # Generar token temporal (válido por 1 hora)
    reset_token_expires = timedelta(hours=1)
    reset_token = create_access_token(
        data={
            "sub": user.email,
            "user_id": user.id,
            "purpose": "password_reset"
        },
        expires_delta=reset_token_expires
    )
    
    # 📧 Enviar email de recuperación
    await send_notification(
        "password-reset",
        {
            "user_email": user.email,
            "user_name": user.nombre,
            "reset_token": reset_token,
            "reset_url": "http://localhost/reset-password"  # URL del frontend
        }
    )
    
    logger.info(f"Email de recuperación enviado a: {user.email}")
    
    return {"message": "Si el email existe, se enviará un enlace de recuperación"}

@app.post("/password-reset/confirm")
async def confirm_password_reset(
    reset_data: PasswordResetConfirm,
    session: Session = Depends(get_session)
):
    """Confirma el restablecimiento de contraseña con el token."""
    
    # Validar longitud de contraseña
    if len(reset_data.new_password) < 8:
        raise HTTPException(
            status_code=400,
            detail="La contraseña debe tener al menos 8 caracteres"
        )
    
    # Verificar token
    try:
        payload = jwt.decode(reset_data.token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        purpose: str = payload.get("purpose")
        
        if purpose != "password_reset":
            raise HTTPException(
                status_code=400,
                detail="Token inválido"
            )
        
        if email is None:
            raise HTTPException(
                status_code=400,
                detail="Token inválido"
            )
    except JWTError:
        raise HTTPException(
            status_code=400,
            detail="Token expirado o inválido"
        )
    
    # Buscar usuario
    user = get_user_by_email(session, email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado"
        )
    
    # Actualizar contraseña
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    user.hashed_password = pwd_context.hash(reset_data.new_password)
    session.add(user)
    session.commit()
    
    logger.info(f"Contraseña restablecida para: {user.email}")
    
    return {"message": "Contraseña restablecida exitosamente"}

@app.get("/health")
def health_check():
    """Endpoint de salud para Docker."""
    return {"status": "ok"}