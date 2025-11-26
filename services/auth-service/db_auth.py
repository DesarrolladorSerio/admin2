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
    telefono: str | None = Field(default=None)     # Teléfono del usuario
    direccion: str | None = Field(default=None)    # Dirección del usuario

class DatosMunicipales(SQLModel, table=True):
    """Datos municipales del ciudadano obtenidos de sistemas externos."""
    __tablename__ = "datos_municipales"
    
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", unique=True)
    rut: str = Field(index=True)
    
    # Licencia de Conducir
    licencia_vigente: bool = Field(default=False)
    licencia_numero: str | None = Field(default=None)
    licencia_fecha_vencimiento: str | None = Field(default=None)
    licencia_categorias: str | None = Field(default=None)  # JSON string
    licencia_multas_pendientes: int = Field(default=0)
    
    # Permisos de Edificación
    permisos_construccion: str | None = Field(default=None)  # JSON string - lista de permisos
    
    # Patentes Comerciales
    patentes_comerciales: str | None = Field(default=None)  # JSON string - lista de patentes
    
    # Juzgado de Policía Local (JPL)
    jpl_multas_pendientes: int = Field(default=0)
    jpl_monto_total_deuda: float = Field(default=0.0)
    jpl_multas: str | None = Field(default=None)  # JSON string - lista de multas
    
    # Servicio de Aseo
    aseo_estado_pago: str = Field(default="al_dia")  # al_dia, moroso
    aseo_deuda_total: float = Field(default=0.0)
    aseo_proximo_vencimiento: str | None = Field(default=None)
    
    # Metadatos
    fecha_ultima_actualizacion: datetime = Field(default_factory=datetime.utcnow)
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow)



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
    # Verificar si ya existe el usuario admin por email O por RUT
    admin_email = "admin@municipalidad.cl"
    admin_rut = "11111111-1"
    
    user_by_email = get_user_by_email(session, admin_email)
    user_by_rut = get_user_by_rut(session, admin_rut)
    
    if not user_by_email and not user_by_rut:
        create_user(
            session, 
            username=admin_email,
            email=admin_email, 
            nombre="Administrador Municipal",
            password="admin123",
            rut=admin_rut,
            role="admin"
        )
        print(f"✅ Usuario admin creado: {admin_email} / admin123")
    else:
        print(f"ℹ️ Usuario admin ya existe (Email: {admin_email}, RUT: {admin_rut})")

# =============================================================================
# FUNCIONES PARA DATOS MUNICIPALES
# =============================================================================

def get_datos_municipales_by_user_id(session: Session, user_id: int) -> DatosMunicipales | None:
    """Obtiene los datos municipales de un usuario por su ID."""
    statement = select(DatosMunicipales).where(DatosMunicipales.user_id == user_id)
    return session.exec(statement).first()

def get_datos_municipales_by_rut(session: Session, rut: str) -> DatosMunicipales | None:
    """Obtiene los datos municipales de un usuario por su RUT."""
    statement = select(DatosMunicipales).where(DatosMunicipales.rut == rut)
    return session.exec(statement).first()

def create_datos_municipales(session: Session, user_id: int, rut: str, datos: dict) -> DatosMunicipales:
    """Crea un registro de datos municipales para un usuario."""
    import json
    
    datos_municipales = DatosMunicipales(
        user_id=user_id,
        rut=rut,
        # Licencia de Conducir
        licencia_vigente=datos.get("licencia", {}).get("vigente", False),
        licencia_numero=datos.get("licencia", {}).get("numero"),
        licencia_fecha_vencimiento=datos.get("licencia", {}).get("fecha_vencimiento"),
        licencia_categorias=json.dumps(datos.get("licencia", {}).get("categorias", [])),
        licencia_multas_pendientes=datos.get("licencia", {}).get("multas_pendientes", 0),
        # Permisos de Edificación
        permisos_construccion=json.dumps(datos.get("permisos_edificacion", [])),
        # Patentes Comerciales
        patentes_comerciales=json.dumps(datos.get("patentes_comerciales", [])),
        # JPL
        jpl_multas_pendientes=len(datos.get("multas_jpl", [])),
        jpl_monto_total_deuda=sum(m.get("monto", 0) for m in datos.get("multas_jpl", [])),
        jpl_multas=json.dumps(datos.get("multas_jpl", [])),
        # Servicio de Aseo
        aseo_estado_pago=datos.get("servicio_aseo", {}).get("estado_pago", "al_dia"),
        aseo_deuda_total=datos.get("servicio_aseo", {}).get("deuda_total", 0.0),
        aseo_proximo_vencimiento=datos.get("servicio_aseo", {}).get("proximo_vencimiento")
    )
    
    session.add(datos_municipales)
    session.commit()
    session.refresh(datos_municipales)
    return datos_municipales

def update_datos_municipales(session: Session, user_id: int, datos: dict) -> DatosMunicipales:
    """Actualiza los datos municipales de un usuario."""
    import json
    
    datos_municipales = get_datos_municipales_by_user_id(session, user_id)
    
    if not datos_municipales:
        # Si no existe, obtener el RUT del usuario y crear
        user = session.get(User, user_id)
        if not user:
            raise ValueError(f"Usuario con ID {user_id} no encontrado")
        return create_datos_municipales(session, user_id, user.rut, datos)
    
    # Actualizar campos existentes
    datos_municipales.licencia_vigente = datos.get("licencia", {}).get("vigente", False)
    datos_municipales.licencia_numero = datos.get("licencia", {}).get("numero")
    datos_municipales.licencia_fecha_vencimiento = datos.get("licencia", {}).get("fecha_vencimiento")
    datos_municipales.licencia_categorias = json.dumps(datos.get("licencia", {}).get("categorias", []))
    datos_municipales.licencia_multas_pendientes = datos.get("licencia", {}).get("multas_pendientes", 0)
    datos_municipales.permisos_construccion = json.dumps(datos.get("permisos_edificacion", []))
    datos_municipales.patentes_comerciales = json.dumps(datos.get("patentes_comerciales", []))
    datos_municipales.jpl_multas_pendientes = len(datos.get("multas_jpl", []))
    datos_municipales.jpl_monto_total_deuda = sum(m.get("monto", 0) for m in datos.get("multas_jpl", []))
    datos_municipales.jpl_multas = json.dumps(datos.get("multas_jpl", []))
    datos_municipales.aseo_estado_pago = datos.get("servicio_aseo", {}).get("estado_pago", "al_dia")
    datos_municipales.aseo_deuda_total = datos.get("servicio_aseo", {}).get("deuda_total", 0.0)
    datos_municipales.aseo_proximo_vencimiento = datos.get("servicio_aseo", {}).get("proximo_vencimiento")
    datos_municipales.fecha_ultima_actualizacion = datetime.utcnow()
    
    session.add(datos_municipales)
    session.commit()
    session.refresh(datos_municipales)
    return datos_municipales