import os
from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import Optional
from datetime import datetime, date

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
    descripcion: str = ""
    estado: str = "activa"  # activa, cancelada, completada
    created_at: datetime = Field(default_factory=datetime.utcnow)

# =============================================================================
# FUNCIONES DE BASE DE DATOS
# =============================================================================

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

def create_reservation(session: Session, reservation_data):
    reservation = Reservation(
        fecha=reservation_data.fecha,
        hora=reservation_data.hora,
        usuario_id=reservation_data.usuario_id,
        usuario_nombre=reservation_data.usuario_nombre,
        descripcion=reservation_data.descripcion
    )
    session.add(reservation)
    session.commit()
    session.refresh(reservation)
    return reservation

def get_all_reservations(session: Session):
    reservations = session.exec(select(Reservation).where(Reservation.estado != "cancelada")).all()
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
