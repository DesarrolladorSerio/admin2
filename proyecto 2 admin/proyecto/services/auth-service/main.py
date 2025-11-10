import logging
from datetime import datetime, timedelta

import httpx
from auth_utils import UserRole, require_role

# Importar funciones de base de datos
from db_auth import (
    EmployeeInfo,
    User,
    authenticate_user,
    create_db_and_tables,
    create_user,
    get_session,
    get_user_by_email,
    get_user_by_rut,
    get_user_by_username,
    init_default_users,
)
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr
from sqlmodel import Session

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

# FastAPI sin middlewares - Nginx maneja CORS y routing
app = FastAPI(
    title="Auth Service",
    description="Servicio de autenticación - CORS manejado por Nginx Gateway",
    version="1.0.0"
)

# NOTA: CORS removido - Nginx API Gateway maneja los headers CORS
# NOTA: Las peticiones llegan pre-procesadas por Nginx con headers correctos
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
    rut: str
    role: str  # Corregido de 'rool' a 'role'

class Token(BaseModel):
    access_token: str
    token_type: str

class EmployeeCreate(BaseModel):
    email: EmailStr
    nombre: str
    rut: str
    password: str
    cargo: str
    departamento: str
    fecha_ingreso: str
    tipo_contrato: str = "planta"  # planta, contrata, honorarios
    
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
        username = payload.get("sub")
        user_id = payload.get("user_id")
        
        if not isinstance(username, str) or not isinstance(user_id, int):
            raise credentials_exception
            
        return {"username": username, "user_id": user_id}
    except JWTError:
        raise credentials_exception

def get_current_user(
    token_data: dict = Depends(verify_token),
    session: Session = Depends(get_session)
) -> User:
    """Obtiene el usuario actual basado en el token."""
    username = token_data["username"]
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
    auth_result = authenticate_user(session, login_data.identifier, login_data.password)
    if not auth_result or isinstance(auth_result, bool):
        login_type_msg = "email" if login_data.login_type == "email" else "RUT"
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Incorrect {login_type_msg} or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # En este punto sabemos que auth_result es un User válido
    user: User = auth_result
    
    if user.id is None or user.email is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Usuario malformado en base de datos"
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
        rut=user_data.rut,
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
# ENDPOINTS DE ADMINISTRACIÓN DE EMPLEADOS
# =============================================================================

@app.post("/admin/employees", response_model=UserResponse)
async def register_employee(
    employee_data: EmployeeCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """Endpoint protegido para que administradores registren empleados municipales."""
    
    # Validar longitud de contraseña
    if len(employee_data.password) < 8:
        raise HTTPException(
            status_code=400,
            detail="La contraseña debe tener al menos 8 caracteres"
        )
    
    # Verificar si el email ya existe
    if get_user_by_email(session, employee_data.email):
        raise HTTPException(
            status_code=400,
            detail="El email ya está registrado"
        )
    
    # Verificar si el RUT ya existe
    if get_user_by_rut(session, employee_data.rut):
        raise HTTPException(
            status_code=400,
            detail="El RUT ya está registrado"
        )
    
    # Crear nuevo empleado
    new_employee = create_user(
        session,
        username=employee_data.email,
        email=employee_data.email,
        nombre=employee_data.nombre,
        password=employee_data.password,
        rut=employee_data.rut,
        role="employee"
    )
    
    # Verificar que los IDs existan
    if new_employee.id is None or current_user.id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al crear empleado"
        )
    
    # Registrar información adicional del empleado
    employee_info = EmployeeInfo(
        user_id=new_employee.id,
        cargo=employee_data.cargo,
        departamento=employee_data.departamento,
        fecha_ingreso=employee_data.fecha_ingreso,
        tipo_contrato=employee_data.tipo_contrato,
        registrado_por=current_user.id
    )
    session.add(employee_info)
    session.commit()
    
    # 📧 Enviar email de bienvenida al empleado
    await send_notification(
        "employee-welcome",
        {
            "user_email": new_employee.email,
            "user_name": new_employee.nombre,
            "cargo": employee_data.cargo,
            "departamento": employee_data.departamento,
            "fecha_ingreso": employee_data.fecha_ingreso
        }
    )
    
    return UserResponse(
        id=new_employee.id,
        username=new_employee.username,
        email=new_employee.email,
        nombre=new_employee.nombre,
        rut=new_employee.rut,
        role=new_employee.role
    )

# =============================================================================
# ENDPOINTS DE USUARIOS (para consulta desde otros servicios)
# =============================================================================

@app.get("/users/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Obtiene la información del usuario autenticado actual."""
    if current_user.id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Usuario sin ID válido"
        )
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        nombre=current_user.nombre,
        rut=current_user.rut,
        role=current_user.role
    )

@app.get("/users", response_model=list[UserResponse])
def get_all_users(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Obtiene todos los usuarios registrados. Solo admin/empleados pueden ver la lista completa."""
    # Verificar permisos
    if current_user.role not in ["admin", "employee"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver la lista de usuarios"
        )
    
    from sqlmodel import select
    statement = select(User).where((User.role == "user") | (User.role == "usuario"))  # Solo usuarios normales
    users = session.exec(statement).all()
    
    return [
        UserResponse(
            id=user.id if user.id is not None else 0,
            username=user.username,
            email=user.email,
            nombre=user.nombre,
            rut=user.rut,
            role=user.role
        )
        for user in users
        if user.id is not None and user.nombre  # Solo usuarios con nombre válido
    ]

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user_by_id(user_id: int, session: Session = Depends(get_session)):
    """Obtiene un usuario específico por ID."""
    from sqlmodel import select
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if user.id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Usuario sin ID válido"
        )
    
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        nombre=user.nombre,
        rut=user.rut,
        role=user.role
    )

@app.get("/verify-user/{user_id}", response_model=UserResponse)
def verify_user_exists(
    user_id: int, 
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Verifica que un usuario existe y retorna información básica (para otros servicios)."""
    from sqlmodel import select
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if user.id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Usuario sin ID válido"
        )
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        nombre=user.nombre,
        rut=user.rut,
        role=user.role
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
        email = payload.get("sub")
        purpose = payload.get("purpose")
        
        if not isinstance(email, str) or not isinstance(purpose, str):
            raise HTTPException(
                status_code=400,
                detail="Token inválido"
            )
        
        if purpose != "password_reset":
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