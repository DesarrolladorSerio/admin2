from sqlmodel import SQLModel, Field, Session, create_engine, select
from datetime import datetime, date, time
from typing import Optional
import os
import httpx

# =============================================================================
# CONFIGURACIÓN DE BASE DE DATOS
# =============================================================================

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:admin@reservations-db:5432/reservations_db")
engine = create_engine(DATABASE_URL)

# URL del servicio de autenticación
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8000")

# =============================================================================
# MODELOS DE BASE DE DATOS
# =============================================================================

class Reservation(SQLModel, table=True):
    """Modelo de reservación"""
    id: int | None = Field(default=None, primary_key=True)
    fecha: date = Field(description="Fecha de la reservación")
    hora: time = Field(description="Hora de la reservación")
    usuario_id: int = Field(description="ID del usuario que reserva")
    usuario_nombre: str = Field(description="Nombre del usuario (cache)")
    descripcion: str = Field(default="", description="Descripción de la reservación")
    estado: str = Field(default="activa", description="Estado: activa, cancelada, completada")
    created_at: datetime = Field(default_factory=datetime.utcnow)

# =============================================================================
# MODELOS PARA API (sin tabla)
# =============================================================================

class UserResponse(SQLModel):
    """Modelo de respuesta para usuarios desde auth-service"""
    id: int
    username: str

# =============================================================================
# FUNCIONES DE BASE DE DATOS
# =============================================================================

def create_db_and_tables():
    """Crea las tablas de la base de datos."""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Generador de sesiones de base de datos."""
    with Session(engine) as session:
        yield session

# =============================================================================
# FUNCIONES PARA CONSULTAR AUTH-SERVICE
# =============================================================================

async def get_all_users() -> list[UserResponse]:
    """Obtiene todos los usuarios desde el servicio de autenticación."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{AUTH_SERVICE_URL}/users")
            if response.status_code == 200:
                users_data = response.json()
                return [UserResponse(**user) for user in users_data]
            return []
    except Exception as e:
        print(f"Error al consultar usuarios: {e}")
        return []

async def get_user_by_id(user_id: int) -> UserResponse | None:
    """Busca un usuario por ID en el servicio de autenticación."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{AUTH_SERVICE_URL}/users/{user_id}")
            if response.status_code == 200:
                user_data = response.json()
                return UserResponse(**user_data)
            return None
    except Exception as e:
        print(f"Error al consultar usuario {user_id}: {e}")
        return None

# =============================================================================
# FUNCIONES DE RESERVACIONES
# =============================================================================

def get_all_reservations(session: Session) -> list[Reservation]:
    """Obtiene todas las reservaciones ordenadas por fecha y hora."""
    statement = select(Reservation).order_by(Reservation.fecha, Reservation.hora)
    return session.exec(statement).all()

def get_reservation_by_id(session: Session, reservation_id: int) -> Reservation | None:
    """Busca una reservación por ID."""
    statement = select(Reservation).where(Reservation.id == reservation_id)
    return session.exec(statement).first()

def create_reservation(session: Session, reservation_data: dict) -> Reservation:
    """Crea una nueva reservación."""
    reservation = Reservation(**reservation_data)
    session.add(reservation)
    session.commit()
    session.refresh(reservation)
    return reservation

def update_reservation(session: Session, reservation_id: int, update_data: dict) -> Reservation | None:
    """Actualiza una reservación existente."""
    reservation = get_reservation_by_id(session, reservation_id)
    if not reservation:
        return None
    
    for key, value in update_data.items():
        if hasattr(reservation, key) and value is not None:
            setattr(reservation, key, value)
    
    session.add(reservation)
    session.commit()
    session.refresh(reservation)
    return reservation

def delete_reservation(session: Session, reservation_id: int) -> bool:
    """Elimina una reservación."""
    reservation = get_reservation_by_id(session, reservation_id)
    if not reservation:
        return False
    
    session.delete(reservation)
    session.commit()
    return True

def get_reservations_by_date_range(session: Session, start_date: date, end_date: date) -> list[Reservation]:
    """Obtiene reservaciones en un rango de fechas (útil para el calendario)."""
    statement = select(Reservation).where(
        Reservation.fecha >= start_date,
        Reservation.fecha <= end_date
    ).order_by(Reservation.fecha, Reservation.hora)
    return session.exec(statement).all()