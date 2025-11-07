from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date
from sqlmodel import Session
import httpx
import logging
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

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    username: str  # Este campo contiene el email del usuario
    user_id: int
    
    @property
    def email(self):
        """Alias para obtener el email (username es el email)"""
        return self.username

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
# FUNCIONES AUXILIARES PARA NOTIFICACIONES
# =============================================================================

async def send_notification(endpoint: str, data: dict):
    """
    Enviar notificación al servicio de notificaciones
    No bloquea si falla, solo registra el error
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                f"http://notifications-service:8004/api/notifications/{endpoint}",
                json=data
            )
            logger.info(f"Notificación enviada: {endpoint} - Status: {response.status_code}")
            return response.json()
    except Exception as e:
        logger.error(f"Error enviando notificación a {endpoint}: {str(e)}")
        return None

# =============================================================================
# ENDPOINTS
# =============================================================================

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "reservations"}

@app.post("/reservations", response_model=ReservationResponse)
async def create_new_reservation(
    reservation_data: ReservationCreate,
    session: Session = Depends(get_session),
    current_user: TokenData = Depends(get_current_user_data_from_token)
):
    if reservation_data.usuario_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes crear una reserva para otro usuario."
        )
    
    # Validar conflictos de horario
    from db_reservas import check_time_conflict
    conflict_result = check_time_conflict(session, reservation_data.fecha, reservation_data.hora, reservation_data.tipo_tramite)
    if conflict_result["has_conflict"]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=conflict_result["message"]
        )
    
    try:
        new_reservation = create_reservation(session, reservation_data)
        
        # Enviar notificación de confirmación (asíncrono, no bloquea)
        await send_notification(
            "reservation/confirmation",
            {
                "user_email": current_user.email,  # Email extraído del token JWT
                "user_name": reservation_data.usuario_nombre,
                "reservation_data": {
                    "id": new_reservation.id,
                    "date": str(new_reservation.fecha),
                    "time": new_reservation.hora,
                    "service": new_reservation.tipo_tramite,
                    "location": "Oficina Principal"  # Puedes parametrizar esto
                }
            }
        )
        
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

    # Validar conflictos de horario si se está cambiando fecha, hora o tipo de trámite
    from db_reservas import check_time_conflict
    update_dict = reservation_update.dict(exclude_unset=True)
    
    if 'fecha' in update_dict or 'hora' in update_dict or 'tipo_tramite' in update_dict:
        nueva_fecha = update_dict.get('fecha', reservation.fecha)
        nueva_hora = update_dict.get('hora', reservation.hora)
        nuevo_tipo = update_dict.get('tipo_tramite', reservation.tipo_tramite)
        
        # Agregar segundos si no están presentes
        if nueva_hora and ':' in nueva_hora and len(nueva_hora.split(':')) == 2:
            nueva_hora += ':00'
        
        conflict_result = check_time_conflict(session, nueva_fecha, nueva_hora, nuevo_tipo, exclude_reservation_id=reservation_id)
        if conflict_result["has_conflict"]:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=conflict_result["message"]
            )

    updated_reservation = update_reservation(session, reservation_id, reservation_update)
    return updated_reservation

@app.delete("/reservations/{reservation_id}")
async def delete_reservation_endpoint(
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

    # Guardar datos para notificación antes de eliminar
    reservation_data = {
        "id": reservation_to_delete.id,
        "date": str(reservation_to_delete.fecha),
        "time": reservation_to_delete.hora,
        "service": reservation_to_delete.tipo_tramite
    }
    user_name = reservation_to_delete.usuario_nombre

    success = delete_reservation(session, reservation_id)
    if not success:
        raise HTTPException(status_code=404, detail="Reservación no encontrada durante la eliminación")
    
    # Enviar notificación de cancelación
    await send_notification(
        "reservation/cancellation",
        {
            "user_email": current_user.email,  # Email extraído del token JWT
            "user_name": user_name,
            "reservation_data": reservation_data
        }
    )
    
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

@app.get("/check-availability/{fecha}/{hora}/{tipo_tramite}")
def check_availability(
    fecha: date,
    hora: str,
    tipo_tramite: str,
    session: Session = Depends(get_session),
    reservation_id: Optional[int] = None
):
    """Verificar si un horario está disponible para reserva"""
    from db_reservas import check_time_conflict
    
    # Agregar segundos si no están presentes
    if ':' in hora and len(hora.split(':')) == 2:
        hora += ':00'
    
    conflict_result = check_time_conflict(session, fecha, hora, tipo_tramite, exclude_reservation_id=reservation_id)
    
    return {
        "available": not conflict_result["has_conflict"],
        "fecha": fecha,
        "hora": hora,
        "tipo_tramite": tipo_tramite,
        "message": conflict_result["message"],
        "conflicting_reservation": conflict_result["conflicting_reservation"]
    }