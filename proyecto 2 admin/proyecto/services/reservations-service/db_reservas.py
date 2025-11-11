import os
from datetime import date, datetime
from typing import Optional

from sqlmodel import Field, Session, SQLModel, create_engine, select

# Configuración de base de datos
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://reservations_user:reservations_password_2024@localhost:5433/reservations_db")

engine = create_engine(DATABASE_URL, echo=True)

# =============================================================================
# MODELOS
# =============================================================================

class Reservation(SQLModel, table=True):
    __tablename__ = "reservations"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    fecha: date
    hora: str
    usuario_id: int # Ya no es una llave foránea
    usuario_nombre: str
    usuario_rut: Optional[str] = None  # RUT del usuario
    usuario_email: Optional[str] = None  # Email del usuario
    usuario_telefono: Optional[str] = None  # Teléfono del usuario
    tipo_tramite: str  # Nuevo campo para el tipo de trámite
    categoria_tramite: Optional[str] = None  # Categoría del trámite
    descripcion: str = ""
    estado: str = "activa"  # activa, cancelada, completada, anulada
    estado_documental: str = "pendiente"  # pendiente, incompleto, completo
    documentos_requeridos: Optional[str] = None  # JSON con lista de documentos
    documentos_cargados: Optional[str] = None  # JSON con lista de documentos subidos
    motivo_anulacion: Optional[str] = None  # Razón de anulación si aplica
    anulada_por: Optional[int] = None  # ID del admin que anuló
    fecha_anulacion: Optional[datetime] = None
    notas_admin: Optional[str] = None  # Notas internas del administrador
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# =============================================================================
# FUNCIONES DE BASE DE DATOS
# =============================================================================

def create_db_and_tables():
    try:
        print("Intentando conectar a la base de datos y crear tablas...")
        SQLModel.metadata.create_all(engine)
        print("Tablas creadas exitosamente o ya existentes.")
    except Exception as e:
        print(f"Error al conectar o crear tablas: {e}")
        raise

def get_session():
    with Session(engine) as session:
        yield session

def create_reservation(session: Session, reservation_data):
    reservation = Reservation(
        fecha=reservation_data.fecha,
        hora=reservation_data.hora,
        usuario_id=reservation_data.usuario_id,
        usuario_nombre=reservation_data.usuario_nombre,
        tipo_tramite=reservation_data.tipo_tramite,
        descripcion=reservation_data.descripcion
    )
    session.add(reservation)
    session.commit()
    session.refresh(reservation)
    return reservation

def get_all_reservations(session: Session):
    reservations = session.exec(
        select(Reservation)
    .where(Reservation.estado != "cancelada")
    .where(Reservation.id is not None)
    ).all()
    return reservations

def get_reservations_by_user(session: Session, user_id: int):
    """Obtiene todas las reservas de un usuario específico"""
    reservations = session.exec(
        select(Reservation)
        .where(Reservation.usuario_id == user_id)
        .where(Reservation.estado != "cancelada")
    ).all()
    return reservations

def get_reservation_by_id(session: Session, reservation_id: int):
    reservation = session.get(Reservation, reservation_id)
    return reservation

def update_reservation(session: Session, reservation_id: int, update_data):
    reservation = session.get(Reservation, reservation_id)
    if not reservation:
        return None
    
    update_dict = update_data.dict(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(reservation, key, value)
    
    session.add(reservation)
    session.commit()
    session.refresh(reservation)
    return reservation

def delete_reservation(session: Session, reservation_id: int):
    reservation = session.get(Reservation, reservation_id)
    if not reservation:
        return False
    
    reservation.estado = "cancelada"
    session.add(reservation)
    session.commit()
    return True

def get_reservations_by_date_range(session: Session, start_date: date, end_date: date):
    reservations = session.exec(
        select(Reservation)
        .where(Reservation.fecha >= start_date)
        .where(Reservation.fecha <= end_date)
        .where(Reservation.estado == "activa")
    ).all()
    return reservations

def get_duration_by_tramite(tipo_tramite: str) -> int:
    """Obtiene la duración en minutos del tipo de trámite"""
    duraciones = {
        "licencia_conducir": 30,
        "permiso_circulacion": 15,
        "certificado_residencia": 10,
        "patente_comercial": 45,
        "permiso_edificacion": 60,
        "registro_civil": 20,
        "subsidios": 40,
        "otros": 30
    }
    return duraciones.get(tipo_tramite, 30)  # Default 30 minutos

def check_time_conflict(session: Session, fecha: date, hora: str, tipo_tramite: str, exclude_reservation_id: Optional[int] = None):
    """
    Verifica si hay conflictos de horario para una nueva reserva
    
    Args:
        session: Sesión de base de datos
        fecha: Fecha de la reserva
        hora: Hora de inicio (formato HH:MM:SS)
        tipo_tramite: Tipo de trámite para calcular duración
        exclude_reservation_id: ID de reserva a excluir (para ediciones)
    
    Returns:
        dict: {"has_conflict": bool, "message": str, "conflicting_reservation": dict}
    """
    from datetime import datetime, timedelta
    
    # Convertir hora string a datetime para cálculos
    hora_inicio = datetime.strptime(hora, "%H:%M:%S").time()
    duracion_minutos = get_duration_by_tramite(tipo_tramite)
    
    # Calcular hora de fin
    datetime_inicio = datetime.combine(fecha, hora_inicio)
    datetime_fin = datetime_inicio + timedelta(minutes=duracion_minutos)
    hora_fin = datetime_fin.time()
    
    # Obtener todas las reservas activas del mismo día
    query = select(Reservation).where(
        Reservation.fecha == fecha,
        Reservation.estado == "activa"
    )
    
    # Excluir la reserva actual si estamos editando
    if exclude_reservation_id:
        query = query.where(Reservation.id != exclude_reservation_id)
    
    reservas_existentes = session.exec(query).all()
    
    # Verificar conflictos con cada reserva existente
    for reserva in reservas_existentes:
        reserva_hora_inicio = datetime.strptime(reserva.hora, "%H:%M:%S").time()
        reserva_duracion = get_duration_by_tramite(reserva.tipo_tramite)
        
        # Calcular hora de fin de la reserva existente
        reserva_datetime_inicio = datetime.combine(fecha, reserva_hora_inicio)
        reserva_datetime_fin = reserva_datetime_inicio + timedelta(minutes=reserva_duracion)
        reserva_hora_fin = reserva_datetime_fin.time()
        
        # Verificar solapamiento
        if (hora_inicio < reserva_hora_fin and hora_fin > reserva_hora_inicio):
            # Formatear horas para el mensaje
            hora_inicio_str = hora_inicio.strftime("%H:%M")
            hora_fin_str = hora_fin.strftime("%H:%M")
            reserva_inicio_str = reserva_hora_inicio.strftime("%H:%M")
            reserva_fin_str = reserva_hora_fin.strftime("%H:%M")
            
            # Obtener nombre del trámite
            tramites_nombres = {
                "licencia_conducir": "Licencia de Conducir",
                "permiso_circulacion": "Permiso de Circulación",
                "certificado_residencia": "Certificado de Residencia",
                "patente_comercial": "Patente Comercial",
                "permiso_edificacion": "Permiso de Edificación",
                "registro_civil": "Registro Civil",
                "subsidios": "Subsidios Municipales",
                "otros": "Otros Trámites"
            }
            
            reserva_tramite_nombre = tramites_nombres.get(reserva.tipo_tramite, reserva.tipo_tramite)
            
            message = f"❌ No puedes reservar a las {hora_inicio_str}. Hay un trámite de '{reserva_tramite_nombre}' programado desde las {reserva_inicio_str} hasta las {reserva_fin_str}. Tu reserva (de {hora_inicio_str} a {hora_fin_str}) genera conflicto. Por favor selecciona otro horario."
            
            return {
                "has_conflict": True,
                "message": message,
                "conflicting_reservation": {
                    "id": reserva.id,
                    "hora_inicio": reserva_inicio_str,
                    "hora_fin": reserva_fin_str,
                    "tipo_tramite": reserva_tramite_nombre,
                    "usuario_nombre": reserva.usuario_nombre
                }
            }
    
    return {
        "has_conflict": False,
        "message": "Horario disponible",
        "conflicting_reservation": None
    }
