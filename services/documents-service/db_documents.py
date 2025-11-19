import os
from datetime import date, datetime
from typing import Optional

from sqlmodel import Field, Session, SQLModel, create_engine, select, col, func

# Configuración de base de datos
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://documents_user:documents_password_2024@localhost:5435/documents_db")

engine = create_engine(DATABASE_URL, echo=True)

# =============================================================================
# MODELOS
# =============================================================================

class DocumentoCiudadano(SQLModel, table=True):
    """Documentos asociados a reservas de ciudadanos"""
    __tablename__ = "documentos_ciudadano"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    reserva_id: Optional[int] = None  # ID de la reserva asociada (opcional)
    usuario_id: int  # ID del usuario
    usuario_rut: str
    tipo_documento: Optional[str] = None  # cedula, certificado_medico, foto, antecedentes, etc.
    nombre_archivo: str
    ruta_archivo: str  # Ruta en almacenamiento
    tamano_bytes: int
    mime_type: str
    estado: str = "pendiente_revision"  # pendiente_revision, aprobado, rechazado
    notas: Optional[str] = None
    digitalizado_por: Optional[int] = None  # ID del digitalizador
    revisado_por: Optional[int] = None  # ID del admin que revisó
    fecha_carga: datetime = Field(default_factory=datetime.utcnow)
    fecha_revision: Optional[datetime] = None

class DocumentoAntiguo(SQLModel, table=True):
    """Documentación antigua del sistema (~100.000 docs)"""
    __tablename__ = "documentos_antiguos"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    numero_expediente: str = Field(index=True)  # Número del expediente antiguo
    ciudadano_rut: Optional[str] = Field(default=None, index=True)
    ciudadano_nombre: Optional[str] = None
    tipo_tramite: str  # Tipo de trámite del documento
    año_tramite: int  # Año del trámite original
    descripcion: str
    numero_fojas: int = 1  # Número de hojas del documento
    nombre_archivo: str
    ruta_archivo: str
    tamano_bytes: int
    estado_digitalizacion: str = "pendiente"  # pendiente, en_proceso, completado
    calidad_digitalizacion: Optional[str] = None  # baja, media, alta
    notas: Optional[str] = None
    digitalizado_por: Optional[int] = None
    fecha_digitalizacion: Optional[datetime] = None
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow)
    
    # Metadatos de catalogación
    palabras_clave: Optional[str] = None  # JSON con keywords para búsqueda
    ubicacion_fisica: Optional[str] = None  # Ubicación del documento físico original

class RegistroDigitalizacion(SQLModel, table=True):
    """Registro diario de avance de digitalización"""
    __tablename__ = "registro_digitalizacion"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    fecha: date = Field(index=True)
    digitalizador_id: int
    digitalizador_nombre: str
    tipo_trabajo: str  # "nuevo" o "antiguo"
    documentos_procesados: int = 0
    paginas_digitalizadas: int = 0
    tiempo_trabajado_minutos: int = 0
    notas: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

# =============================================================================
# FUNCIONES DE BASE DE DATOS
# =============================================================================

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

# =============================================================================
# DOCUMENTOS CIUDADANO
# =============================================================================

def create_documento_ciudadano(session: Session, doc_data):
    documento = DocumentoCiudadano(**doc_data.dict())
    session.add(documento)
    session.commit()
    session.refresh(documento)
    return documento

def get_documentos_by_reserva(session: Session, reserva_id: int):
    docs = session.exec(
        select(DocumentoCiudadano).where(DocumentoCiudadano.reserva_id == reserva_id)
    ).all()
    return docs

def get_documentos_by_usuario(session: Session, usuario_id: int):
    docs = session.exec(
        select(DocumentoCiudadano).where(DocumentoCiudadano.usuario_id == usuario_id)
    ).all()
    return docs

def update_documento_estado(session: Session, documento_id: int, estado: str, revisado_por: int, notas: Optional[str] = None):
    documento = session.get(DocumentoCiudadano, documento_id)
    if not documento:
        return None
    
    documento.estado = estado
    documento.revisado_por = revisado_por
    documento.fecha_revision = datetime.utcnow()
    if notas:
        documento.notas = notas
    
    session.add(documento)
    session.commit()
    session.refresh(documento)
    return documento

# =============================================================================
# DOCUMENTOS ANTIGUOS
# =============================================================================

def create_documento_antiguo(session: Session, doc_data):
    documento = DocumentoAntiguo(**doc_data.dict())
    session.add(documento)
    session.commit()
    session.refresh(documento)
    return documento

def get_documentos_antiguos_pendientes(session: Session, limit: int = 50):
    """Obtiene documentos antiguos pendientes de digitalizar"""
    docs = session.exec(
        select(DocumentoAntiguo)
        .where(DocumentoAntiguo.estado_digitalizacion == "pendiente")
        .limit(limit)
    ).all()
    return docs

def update_documento_antiguo(session: Session, doc_id: int, update_data: dict):
    documento = session.get(DocumentoAntiguo, doc_id)
    if not documento:
        return None
    
    for key, value in update_data.items():
        setattr(documento, key, value)
    
    session.add(documento)
    session.commit()
    session.refresh(documento)
    return documento

def buscar_documentos_antiguos(
    session: Session, 
    rut: Optional[str] = None,
    nombre: Optional[str] = None,
    expediente: Optional[str] = None,
    año: Optional[int] = None,
    tipo_tramite: Optional[str] = None,
    skip: int = 0,
    limit: int = 50
):
    """Búsqueda avanzada de documentos antiguos"""
    query = select(DocumentoAntiguo)
    
    if rut:
        query = query.where(DocumentoAntiguo.ciudadano_rut.contains(rut))
    if nombre:
        query = query.where(DocumentoAntiguo.ciudadano_nombre.ilike(f"%{nombre}%"))
    if expediente:
        query = query.where(DocumentoAntiguo.numero_expediente.contains(expediente))
    if año:
        query = query.where(DocumentoAntiguo.año_tramite == año)
    if tipo_tramite:
        query = query.where(DocumentoAntiguo.tipo_tramite == tipo_tramite)
    
    docs = session.exec(query.offset(skip).limit(limit)).all()
    return docs

# =============================================================================
# REGISTRO DIGITALIZACION
# =============================================================================

def create_registro_digitalizacion(session: Session, registro_data):
    registro = RegistroDigitalizacion(**registro_data.dict())
    session.add(registro)
    session.commit()
    session.refresh(registro)
    return registro

def get_registros_por_fecha(session: Session, fecha_inicio: date, fecha_fin: date):
    """Obtiene registros de digitalización en un rango de fechas"""
    registros = session.exec(
        select(RegistroDigitalizacion)
        .where(RegistroDigitalizacion.fecha >= fecha_inicio)
        .where(RegistroDigitalizacion.fecha <= fecha_fin)
    ).all()
    return registros

def get_estadisticas_digitalizacion(session: Session, fecha_inicio: date, fecha_fin: date):
    """Genera estadísticas de digitalización"""
    # Total de documentos procesados
    result = session.exec(
        select(
            func.sum(RegistroDigitalizacion.documentos_procesados),
            func.sum(RegistroDigitalizacion.paginas_digitalizadas),
            func.sum(RegistroDigitalizacion.tiempo_trabajado_minutos)
        )
        .where(RegistroDigitalizacion.fecha >= fecha_inicio)
        .where(RegistroDigitalizacion.fecha <= fecha_fin)
    ).first()
    
    return {
        "documentos_procesados": result[0] or 0,
        "paginas_digitalizadas": result[1] or 0,
        "tiempo_trabajado_minutos": result[2] or 0
    }

def get_avance_digitalizacion_antigua(session: Session):
    """Obtiene el progreso de digitalización de documentos antiguos"""
    total = session.exec(
        select(func.count()).select_from(DocumentoAntiguo)
    ).one()
    
    completados = session.exec(
        select(func.count())
        .select_from(DocumentoAntiguo)
        .where(DocumentoAntiguo.estado_digitalizacion == "completado")
    ).one()
    
    en_proceso = session.exec(
        select(func.count())
        .select_from(DocumentoAntiguo)
        .where(DocumentoAntiguo.estado_digitalizacion == "en_proceso")
    ).one()
    
    return {
        "total": total,
        "completados": completados,
        "en_proceso": en_proceso,
        "pendientes": total - completados - en_proceso,
        "porcentaje_completado": (completados / total * 100) if total > 0 else 0
    }
