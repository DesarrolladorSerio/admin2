import os
from datetime import datetime

from passlib.context import CryptContext
from sqlmodel import Field, Session, SQLModel, create_engine, select

# =============================================================================
# CONFIGURACIÓN DE BASE DE DATOS
# =============================================================================

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:admin@db:5432/proyecto_db")
engine = create_engine(DATABASE_URL) #funcion model slq . coneccion logica y monotr 
#ahora traducimos lenguaje postgresql a python 

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#compara contraseña de ususarioc on un hash ingresado 
# =============================================================================
# MODELOS DE BASE DE DATOS
# =============================================================================

class EmployeeInfo(SQLModel, table=True):
    """Información adicional específica para empleados municipales."""
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    cargo: str
    departamento: str
    fecha_ingreso: str
    tipo_contrato: str  # planta, contrata, honorarios
    registrado_por: int = Field(foreign_key="user.id")
    fecha_registro: datetime = Field(default_factory=datetime.utcnow)

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)  # Mantener para compatibilidad
    email: str = Field(index=True, unique=True)     # Email único
    rut: str = Field(index=True, unique=True)       # RUT único y OBLIGATORIO
    nombre: str = Field(default="user")
    hashed_password: str = Field()                  # Contraseña hasheada
    role: str = Field(default="user")              # Rol del usuario (admin, user, employee)



# =============================================================================
# FUNCIONES DE BASE DE DATOS
# =============================================================================

def create_db_and_tables(): #usar esquema de modelo user definido previamente
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

def get_user_by_email(session: Session, email: str) -> User | None:
    """Busca un usuario por su email."""
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()

def get_user_by_rut(session: Session, rut: str) -> User | None:
    """Busca un usuario por su RUT."""
    statement = select(User).where(User.rut == rut)
    return session.exec(statement).first()

def get_user_by_role(session: Session, role: str) -> User | None:
    statement = select(User).where(User.role == role)
    return session.exec(statement).first()

def get_user_by_login_identifier(session: Session, identifier: str) -> User | None:
    """Busca un usuario por email, RUT o username."""
    # Intentar por email
    user = get_user_by_email(session, identifier)
    if user:
        return user
    
    # Intentar por RUT
    user = get_user_by_rut(session, identifier)
    if user:
        return user
    
    # Intentar por username (compatibilidad)
    return get_user_by_username(session, identifier)

def create_user(session: Session, username: str, email: str, nombre: str, password: str, rut: str, role: str = "user") -> User:
    """Crea un nuevo usuario en la base de datos."""
    hashed_password = pwd_context.hash(password)
    db_user = User(
        username=username,
        email=email,
        rut=rut,
        nombre=nombre,
        hashed_password=hashed_password,
        role=role
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

def authenticate_user(session: Session, identifier: str, password: str) -> User | bool:
    """Autentica un usuario verificando su contraseña. Acepta email, RUT o username."""
    user = get_user_by_login_identifier(session, identifier)
    if not user:
        return False
    if not pwd_context.verify(password, user.hashed_password):
        return False
    return user

def init_default_users(session: Session):
    """Inicializa usuarios por defecto si no existen."""
    # Verificar si ya existe el usuario admin
    admin_user = get_user_by_email(session, "admin@municipalidad.cl")
    if not admin_user:
        create_user(
            session, 
            username="admin@municipalidad.cl",
            email="admin@municipalidad.cl", 
            nombre="Administrador Municipal",
            password="sysadmin",
            rut="11111111-1",
            role="admin"
        )
        print("✅ Usuario admin creado: admin@municipalidad.cl / admin123")