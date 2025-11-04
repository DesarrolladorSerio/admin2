from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session
from datetime import datetime, date, time
from pydantic import BaseModel
from typing import Optional

# Importar funciones de base de datos
from db_reservas import (
    create_db_and_tables,
    get_session,
    get_all_users,
    get_user_by_id,
    get_all_reservations,
    get_reservation_by_id,
    create_reservation,
    update_reservation,
    delete_reservation,
    get_reservations_by_date_range,
    Reservation,
    UserResponse
)

# =============================================================================
# CONFIGURACIÓN DE LA APP
# =============================================================================

app = FastAPI(title="Reservations API", version="1.0.0")

# Habilitar CORS para desarrollo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios exactos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# MODELOS DE PYDANTIC (REQUEST/RESPONSE)
# =============================================================================

class ReservationCreate(BaseModel):
    """Modelo para crear nuevas reservaciones"""
    fecha: date
    hora: time
    usuario_id: int
    usuario_nombre: str
    descripcion: str = ""

class ReservationUpdate(BaseModel):
    """Modelo para actualizar reservaciones (campos opcionales)"""
    fecha: Optional[date] = None
    hora: Optional[time] = None
    descripcion: Optional[str] = None
    estado: Optional[str] = None

class ReservationResponse(BaseModel):
    """Modelo de respuesta para reservaciones"""
    id: int
    fecha: date
    hora: time
    usuario_id: int
    usuario_nombre: str
    descripcion: str
    estado: str
    created_at: datetime

class UserResponse(BaseModel):
    """Modelo de respuesta para usuarios"""
    id: int
    username: str

# =============================================================================
# EVENTOS DE APLICACIÓN
# =============================================================================

@app.on_event("startup")
def on_startup():
    """Inicializa la base de datos al arrancar la aplicación."""
    create_db_and_tables()
    print("✅ Reservations Service iniciado")

# =============================================================================
# ENDPOINTS DE LA API
# =============================================================================

@app.get("/health")
def health_check():
    """Endpoint de salud para Docker."""
    return {"status": "ok", "service": "reservations"}

# ===== ENDPOINTS DE USUARIOS =====

@app.get("/users", response_model=list[UserResponse])
async def get_users():
    """Obtiene la lista de todos los usuarios desde auth-service."""
    users = await get_all_users()
    return users

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    """Obtiene un usuario específico por ID desde auth-service."""
    user = await get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

# ===== ENDPOINTS DE RESERVACIONES =====

@app.get("/reservations", response_model=list[ReservationResponse])
def get_reservations(session: Session = Depends(get_session)):
    """Obtiene todas las reservaciones."""
    reservations = get_all_reservations(session)
    return [
        ReservationResponse(
            id=r.id,
            fecha=r.fecha,
            hora=r.hora,
            usuario_id=r.usuario_id,
            usuario_nombre=r.usuario_nombre,
            descripcion=r.descripcion,
            estado=r.estado,
            created_at=r.created_at
        ) for r in reservations
    ]

@app.get("/reservations/{reservation_id}", response_model=ReservationResponse)
def get_reservation(reservation_id: int, session: Session = Depends(get_session)):
    """Obtiene una reservación específica por ID."""
    reservation = get_reservation_by_id(session, reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservación no encontrada")
    
    return ReservationResponse(
        id=reservation.id,
        fecha=reservation.fecha,
        hora=reservation.hora,
        usuario_id=reservation.usuario_id,
        usuario_nombre=reservation.usuario_nombre,
        descripcion=reservation.descripcion,
        estado=reservation.estado,
        created_at=reservation.created_at
    )

@app.post("/reservations", response_model=ReservationResponse)
def create_new_reservation(
    reservation_data: ReservationCreate,
    session: Session = Depends(get_session)
):
    """Crea una nueva reservación."""
    # Verificar que el usuario existe
    user = get_user_by_id(session, reservation_data.usuario_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Crear la reservación
    reservation = create_reservation(
        session,
        reservation_data.dict()
    )
    
    return ReservationResponse(
        id=reservation.id,
        fecha=reservation.fecha,
        hora=reservation.hora,
        usuario_id=reservation.usuario_id,
        usuario_nombre=reservation.usuario_nombre,
        descripcion=reservation.descripcion,
        estado=reservation.estado,
        created_at=reservation.created_at
    )

@app.put("/reservations/{reservation_id}", response_model=ReservationResponse)
def update_existing_reservation(
    reservation_id: int,
    update_data: ReservationUpdate,
    session: Session = Depends(get_session)
):
    """Actualiza una reservación existente."""
    reservation = update_reservation(
        session,
        reservation_id,
        update_data.dict(exclude_unset=True)
    )
    
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservación no encontrada")
    
    return ReservationResponse(
        id=reservation.id,
        fecha=reservation.fecha,
        hora=reservation.hora,
        usuario_id=reservation.usuario_id,
        usuario_nombre=reservation.usuario_nombre,
        descripcion=reservation.descripcion,
        estado=reservation.estado,
        created_at=reservation.created_at
    )

@app.delete("/reservations/{reservation_id}")
def delete_existing_reservation(
    reservation_id: int,
    session: Session = Depends(get_session)
):
    """Elimina una reservación."""
    success = delete_reservation(session, reservation_id)
    if not success:
        raise HTTPException(status_code=404, detail="Reservación no encontrada")
    
    return {"message": "Reservación eliminada exitosamente"}

@app.get("/reservations/calendar/{start_date}/{end_date}", response_model=list[ReservationResponse])
def get_calendar_reservations(
    start_date: date,
    end_date: date,
    session: Session = Depends(get_session)
):
    """Obtiene reservaciones para un rango de fechas (útil para calendario)."""
    reservations = get_reservations_by_date_range(session, start_date, end_date)
    return [
        ReservationResponse(
            id=r.id,
            fecha=r.fecha,
            hora=r.hora,
            usuario_id=r.usuario_id,
            usuario_nombre=r.usuario_nombre,
            descripcion=r.descripcion,
            estado=r.estado,
            created_at=r.created_at
        ) for r in reservations
    ]