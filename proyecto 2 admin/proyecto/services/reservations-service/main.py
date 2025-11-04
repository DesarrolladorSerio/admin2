from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date
from sqlmodel import Session
from db_reservas import (
    create_db_and_tables,
    get_session,
    create_reservation,
    get_all_reservations,
    get_reservation_by_id,
    update_reservation,
    delete_reservation,
    get_reservations_by_date_range,
    get_all_users,
    Reservation,
    User
)

app = FastAPI(title="Reservations API")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# MODELOS DE DATOS (Pydantic)
# =============================================================================

class ReservationCreate(BaseModel):
    fecha: date
    hora: str
    usuario_id: int
    usuario_nombre: str
    descripcion: Optional[str] = ""

class ReservationUpdate(BaseModel):
    fecha: Optional[date] = None
    hora: Optional[str] = None
    usuario_id: Optional[int] = None
    usuario_nombre: Optional[str] = None
    descripcion: Optional[str] = None
    estado: Optional[str] = None

class ReservationResponse(BaseModel):
    id: int
    fecha: date
    hora: str
    usuario_id: int
    usuario_nombre: str
    descripcion: str
    estado: str
    created_at: datetime

class UserResponse(BaseModel):
    id: int
    username: str

# =============================================================================
# EVENTOS
# =============================================================================

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    print("✅ Base de datos de reservaciones inicializada")

# =============================================================================
# ENDPOINTS
# =============================================================================

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "reservations"}

@app.get("/users", response_model=List[UserResponse])
def get_users(session: Session = Depends(get_session)):
    users = get_all_users(session)
    return users

@app.post("/reservations", response_model=ReservationResponse)
def create_new_reservation(
    reservation: ReservationCreate,
    session: Session = Depends(get_session)
):
    try:
        new_reservation = create_reservation(session, reservation)
        return new_reservation
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/reservations", response_model=List[ReservationResponse])
def get_reservations(session: Session = Depends(get_session)):
    reservations = get_all_reservations(session)
    return reservations

@app.get("/reservations/{reservation_id}", response_model=ReservationResponse)
def get_reservation(reservation_id: int, session: Session = Depends(get_session)):
    reservation = get_reservation_by_id(session, reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservación no encontrada")
    return reservation

@app.put("/reservations/{reservation_id}", response_model=ReservationResponse)
def update_reservation_endpoint(
    reservation_id: int,
    reservation_update: ReservationUpdate,
    session: Session = Depends(get_session)
):
    reservation = update_reservation(session, reservation_id, reservation_update)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservación no encontrada")
    return reservation

@app.delete("/reservations/{reservation_id}")
def delete_reservation_endpoint(
    reservation_id: int,
    session: Session = Depends(get_session)
):
    success = delete_reservation(session, reservation_id)
    if not success:
        raise HTTPException(status_code=404, detail="Reservación no encontrada")
    return {"message": "Reservación eliminada exitosamente"}

@app.get("/reservations/calendar/{start_date}/{end_date}", response_model=List[ReservationResponse])
def get_calendar_reservations(
    start_date: date,
    end_date: date,
    session: Session = Depends(get_session)
):
    reservations = get_reservations_by_date_range(session, start_date, end_date)
    return reservations

