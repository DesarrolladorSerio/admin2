from sqlmodel import SQLModel, Field, Session, create_engine, select
from passlib.context import CryptContext
import os

# =============================================================================
# CONFIGURACIÓN DE BASE DE DATOS
# =============================================================================

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:admin@db:5432/proyecto_db")
engine = create_engine(DATABASE_URL)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# =============================================================================
# MODELOS DE BASE DE DATOS
# =============================================================================

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    hashed_password: str

# =============================================================================
# FUNCIONES DE BASE DE DATOS
# =============================================================================

def create_db_and_tables():
    """Crea las tablas de la base de datos."""
    try:
        SQLModel.metadata.create_all(engine, checkfirst=True)
    except Exception as e:
        print(f"⚠️ Advertencia al crear tablas: {e}")
        # Las tablas probablemente ya existen, continuar

def get_session():
    """Generador de sesiones de base de datos."""
    with Session(engine) as session:
        yield session

def get_user_by_username(session: Session, username: str) -> User | None:
    """Busca un usuario por su nombre de usuario."""
    statement = select(User).where(User.username == username)
    return session.exec(statement).first()

def create_user(session: Session, username: str, password: str) -> User:
    """Crea un nuevo usuario en la base de datos."""
    hashed_password = pwd_context.hash(password)
    db_user = User(username=username, hashed_password=hashed_password)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

def authenticate_user(session: Session, username: str, password: str) -> User | bool:
    """Autentica un usuario verificando su contraseña."""
    user = get_user_by_username(session, username)
    if not user:
        return False
    if not pwd_context.verify(password, user.hashed_password):
        return False
    return user

def init_default_users(session: Session):
    """Inicializa usuarios por defecto si no existen."""
    # Verificar si ya existe el usuario admin
    admin_user = get_user_by_username(session, "admin@municipalidad.cl")
    if not admin_user:
        create_user(session, "admin@municipalidad.cl", "admin123")
        print("✅ Usuario admin creado: admin@municipalidad.cl / admin123")