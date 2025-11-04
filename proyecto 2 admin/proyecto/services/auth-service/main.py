from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from pydantic import BaseModel
from sqlmodel import Session

# Importar funciones de base de datos
from db_auth import (
    create_db_and_tables, 
    get_session, 
    authenticate_user,
    init_default_users,
    get_user_by_username,
    User
)

# =============================================================================
# CONFIGURACIÓN
# =============================================================================

SECRET_KEY = "un-secreto-muy-fuerte-y-largo"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()
# =============================================================================
# MODELOS DE DATOS (Pydantic)
# =============================================================================
class LoginRequest(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str

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
# ENDPOINTS DE LA API
# =============================================================================

@app.post("/token", response_model=Token)
async def login_for_access_token(
    login_data: LoginRequest,
    session: Session = Depends(get_session)
):
    """Endpoint para el login con JSON."""
    user = authenticate_user(session, login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/register", response_model=Token)
def register_user(
    user_data: UserCreate,
    session: Session = Depends(get_session)
):
    """Registra un nuevo usuario."""
    from db_auth import get_user_by_username, create_user
    
    # Verificar si el usuario ya existe
    existing_user = get_user_by_username(session, user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="El usuario ya existe"
        )
    
    # Crear nuevo usuario
    new_user = create_user(session, user_data.username, user_data.password)
    
    # Crear token automáticamente
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": new_user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# =============================================================================
# ENDPOINTS DE USUARIOS (para consulta desde otros servicios)
# =============================================================================

@app.get("/users", response_model=list[UserResponse])
def get_all_users(session: Session = Depends(get_session)):
    """Obtiene todos los usuarios registrados."""
    from sqlmodel import select
    statement = select(User)
    users = session.exec(statement).all()
    return [UserResponse(id=user.id, username=user.username) for user in users]

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user_by_id(user_id: int, session: Session = Depends(get_session)):
    """Obtiene un usuario específico por ID."""
    from sqlmodel import select
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return UserResponse(id=user.id, username=user.username)

@app.get("/health")
def health_check():
    """Endpoint de salud para Docker."""
    return {"status": "ok"}