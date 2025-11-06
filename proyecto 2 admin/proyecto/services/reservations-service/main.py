from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
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
    Reservation
)

# =============================================================================
# CONFIGURACIÓN DE AUTENTICACIÓN
# =============================================================================
SECRET_KEY = "un-secreto-muy-fuerte-y-largo"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

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
# MODELOS Y FUNCIONES DE AUTENTICACIÓN
# =============================================================================

class TokenData(BaseModel):
    username: str
    user_id: int

def get_current_user_data_from_token(token: str = Depends(oauth2_scheme)) -> TokenData:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        if username is None or user_id is None:
            raise credentials_exception
        return TokenData(username=username, user_id=user_id)
    except JWTError:
        raise credentials_exception

# =============================================================================
# MODELOS DE DATOS (Pydantic)
# =============================================================================

class ReservationCreate(BaseModel):
    fecha: date
    hora: str
    usuario_id: int
    usuario_nombre: str
    tipo_tramite: str  # Nuevo campo para el tipo de trámite
    descripcion: Optional[str] = ""

class ReservationUpdate(BaseModel):
    fecha: Optional[date] = None
    hora: Optional[str] = None
    tipo_tramite: Optional[str] = None  # Permitir actualizar el tipo de trámite
    descripcion: Optional[str] = None

class ReservationResponse(BaseModel):
    id: int
    fecha: date
    hora: str
    usuario_id: int
    usuario_nombre: str
    tipo_tramite: str  # Nuevo campo en la respuesta
    descripcion: str
    estado: str
    created_at: datetime

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

@app.post("/reservations", response_model=ReservationResponse)
def create_new_reservation(
    reservation_data: ReservationCreate,
    session: Session = Depends(get_session),
    current_user: TokenData = Depends(get_current_user_data_from_token)
):
    if reservation_data.usuario_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes crear una reserva para otro usuario."
        )
    try:
        new_reservation = create_reservation(session, reservation_data)
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
    session: Session = Depends(get_session),
    current_user: TokenData = Depends(get_current_user_data_from_token)
):
    reservation = get_reservation_by_id(session, reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservación no encontrada")
    
    if reservation.usuario_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para editar esta reservación."
        )

    updated_reservation = update_reservation(session, reservation_id, reservation_update)
    return updated_reservation

@app.delete("/reservations/{reservation_id}")
def delete_reservation_endpoint(
    reservation_id: int,
    session: Session = Depends(get_session),
    current_user: TokenData = Depends(get_current_user_data_from_token)
):
    reservation_to_delete = get_reservation_by_id(session, reservation_id)

    if not reservation_to_delete:
        raise HTTPException(status_code=404, detail="Reservación no encontrada")

    if reservation_to_delete.usuario_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="No tienes permiso para eliminar esta reservación."
        )

    success = delete_reservation(session, reservation_id)
    if not success:
        raise HTTPException(status_code=404, detail="Reservación no encontrada durante la eliminación")
    return {"message": "Reservación eliminada exitosamente"}

@app.get("/reservations/calendar/{start_date}/{end_date}", response_model=List[ReservationResponse])
def get_calendar_reservations(
    start_date: date,
    end_date: date,
    session: Session = Depends(get_session)
):
    reservations = get_reservations_by_date_range(session, start_date, end_date)
    return reservations

@app.get("/tipos-tramites")
def get_tipos_tramites():
    """Obtener los tipos de trámites disponibles en la municipalidad"""
    tipos_tramites = [
        {
            "id": "licencia_conducir",
            "nombre": "Licencia de Conducir",
            "descripcion": "Obtención o renovación de licencia de conducir",
            "duracion_estimada": "30 minutos"
        },
        {
            "id": "permiso_circulacion",
            "nombre": "Permiso de Circulación",
            "descripcion": "Trámite de permiso de circulación vehicular",
            "duracion_estimada": "15 minutos"
        },
        {
            "id": "certificado_residencia",
            "nombre": "Certificado de Residencia",
            "descripcion": "Certificado que acredita residencia en la comuna",
            "duracion_estimada": "10 minutos"
        },
        {
            "id": "patente_comercial",
            "nombre": "Patente Comercial",
            "descripcion": "Solicitud o renovación de patente comercial",
            "duracion_estimada": "45 minutos"
        },
        {
            "id": "permiso_edificacion",
            "nombre": "Permiso de Edificación",
            "descripcion": "Permisos para construcción y edificación",
            "duracion_estimada": "60 minutos"
        },
        {
            "id": "registro_civil",
            "nombre": "Registro Civil",
            "descripcion": "Trámites de registro civil (certificados, matrimonio, etc.)",
            "duracion_estimada": "20 minutos"
        },
        {
            "id": "subsidios",
            "nombre": "Subsidios Municipales",
            "descripcion": "Solicitud de subsidios y beneficios municipales",
            "duracion_estimada": "40 minutos"
        },
        {
            "id": "otros",
            "nombre": "Otros Trámites",
            "descripcion": "Otros trámites municipales no especificados",
            "duracion_estimada": "30 minutos"
        }
    ]
    return tipos_tramites