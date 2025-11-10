import logging
from datetime import date, datetime
from typing import Any, Dict, List, Optional

import httpx
from auth_utils import get_current_user
from db_reservas import (
    create_db_and_tables,
    create_reservation,
    delete_reservation,
    get_all_reservations,
    get_reservation_by_id,
    get_reservations_by_date_range,
    get_session,
    update_reservation,
)
from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI sin middlewares - Nginx maneja CORS y routing
app = FastAPI(
    title="Reservations API",
    description="Servicio de reservaciones - CORS manejado por Nginx Gateway",
    version="1.0.0"
)

# NOTA: CORS removido - Nginx API Gateway maneja los headers CORS

# =============================================================================
# CONFIGURACIÓN DE LA APLICACIÓN
# =============================================================================

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

class ReservationDetailedResponse(BaseModel):
    """Respuesta con información detallada para admin/empleados"""
    id: int
    fecha: date
    hora: str
    usuario_id: int
    usuario_nombre: str
    usuario_email: Optional[str] = None  # Información adicional del usuario
    usuario_telefono: Optional[str] = None
    tipo_tramite: str
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
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    if reservation_data.usuario_id != current_user["id"]:
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
                "user_email": current_user["email"],  # Email extraído del token JWT
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
def get_reservations(
    session: Session = Depends(get_session),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Obtener TODAS las reservaciones para TODOS los usuarios.
    Todos pueden ver el calendario completo, pero solo pueden 
    modificar/eliminar según sus permisos (verificado en endpoints PUT/DELETE).
    """
    # Todos los usuarios ven todas las reservas
    reservations = get_all_reservations(session)
    return reservations

@app.get("/reservations/my", response_model=List[ReservationResponse])
def get_my_reservations(
    session: Session = Depends(get_session),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Obtener solo las reservaciones del usuario actual.
    Endpoint específico si se necesita filtrar.
    """
    from db_reservas import get_reservations_by_user
    reservations = get_reservations_by_user(session, current_user["id"])
    return reservations

@app.get("/reservations/{reservation_id}", response_model=ReservationResponse)
def get_reservation(
    reservation_id: int, 
    session: Session = Depends(get_session),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    reservation = get_reservation_by_id(session, reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservación no encontrada")
    
    # Verificar permisos: admin/empleado pueden ver cualquier reserva, usuarios solo las suyas
    user_role = current_user.get("role", "user")
    if user_role not in ["admin", "employee"] and reservation.usuario_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver esta reservación."
        )
    
    return reservation

@app.put("/reservations/{reservation_id}", response_model=ReservationResponse)
def update_reservation_endpoint(
    reservation_id: int,
    reservation_update: ReservationUpdate,
    session: Session = Depends(get_session),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    reservation = get_reservation_by_id(session, reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservación no encontrada")
    
    # Verificar permisos: admin/empleado pueden editar cualquier reserva, usuarios solo las suyas
    user_role = current_user.get("role", "user")
    if user_role not in ["admin", "employee"] and reservation.usuario_id != current_user["id"]:
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
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    reservation_to_delete = get_reservation_by_id(session, reservation_id)

    if not reservation_to_delete:
        raise HTTPException(status_code=404, detail="Reservación no encontrada")

    # Verificar permisos: admin/empleado pueden eliminar cualquier reserva, usuarios solo las suyas
    user_role = current_user.get("role", "user")
    if user_role not in ["admin", "employee"] and reservation_to_delete.usuario_id != current_user["id"]:
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
            "user_email": current_user["email"],  # Email extraído del token JWT
            "user_name": user_name,
            "reservation_data": reservation_data
        }
    )
    
    return {"message": "Reservación eliminada exitosamente"}

@app.get("/admin/reservations", response_model=List[ReservationDetailedResponse])
async def get_all_reservations_detailed(
    session: Session = Depends(get_session),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Endpoint exclusivo para admin/empleados para obtener todas las reservas con información detallada de usuarios
    """
    user_role = current_user.get("role", "user")
    if user_role not in ["admin", "employee"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Se requiere rol de administrador o empleado."
        )
    
    reservations = get_all_reservations(session)
    detailed_reservations = []
    
    # Enriquecer cada reserva con información del usuario desde el servicio de auth
    for reservation in reservations:
        detailed_reservation = ReservationDetailedResponse(
            id=reservation.id or 0,  # Manejo del caso nullable
            fecha=reservation.fecha,
            hora=reservation.hora,
            usuario_id=reservation.usuario_id,
            usuario_nombre=reservation.usuario_nombre,
            tipo_tramite=reservation.tipo_tramite,
            descripcion=reservation.descripcion,
            estado=reservation.estado,
            created_at=reservation.created_at
        )
        
        # Intentar obtener información adicional del usuario
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"http://auth-service:8001/api/auth/user/{reservation.usuario_id}",
                    headers={"Authorization": f"Bearer {current_user.get('token', '')}"}
                )
                
                if response.status_code == 200:
                    user_data = response.json()
                    detailed_reservation.usuario_email = user_data.get("email", "")
                    # Agregar más campos si están disponibles en el servicio de auth
                    
        except Exception as e:
            logger.warning(f"No se pudo obtener información del usuario {reservation.usuario_id}: {e}")
        
        detailed_reservations.append(detailed_reservation)
    
    return detailed_reservations

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
        # PRIMER OTORGAMIENTO - NO PROFESIONALES
        {
            "id": "primer_otorg_clase_b",
            "nombre": "Primer Otorgamiento - Clase B (Autos)",
            "categoria": "primer_otorgamiento",
            "descripcion": "Primera licencia para conducir automóviles",
            "duracion_estimada": "45 minutos"
        },
        {
            "id": "primer_otorg_clase_c",
            "nombre": "Primer Otorgamiento - Clase C (Motos)",
            "categoria": "primer_otorgamiento",
            "descripcion": "Primera licencia para conducir motocicletas",
            "duracion_estimada": "40 minutos"
        },
        {
            "id": "primer_otorg_clase_cr",
            "nombre": "Primer Otorgamiento - Clase CR (Triciclos)",
            "categoria": "primer_otorgamiento",
            "descripcion": "Licencia para triciclos motorizados de carga",
            "duracion_estimada": "30 minutos"
        },
        {
            "id": "primer_otorg_clase_b_17",
            "nombre": "Primer Otorgamiento - Clase B (17 años)",
            "categoria": "primer_otorgamiento",
            "descripcion": "Licencia clase B para menores de 18 años",
            "duracion_estimada": "50 minutos"
        },
        
        # PRIMER OTORGAMIENTO - ESPECIALES
        {
            "id": "primer_otorg_clase_d",
            "nombre": "Primer Otorgamiento - Clase D (Maquinaria)",
            "categoria": "primer_otorgamiento",
            "descripcion": "Licencia para operar maquinaria pesada",
            "duracion_estimada": "40 minutos"
        },
        {
            "id": "primer_otorg_clase_e",
            "nombre": "Primer Otorgamiento - Clase E (Tracción Animal)",
            "categoria": "primer_otorgamiento",
            "descripcion": "Licencia para vehículos de tracción animal",
            "duracion_estimada": "30 minutos"
        },
        {
            "id": "primer_otorg_clase_f",
            "nombre": "Primer Otorgamiento - Clase F",
            "categoria": "primer_otorgamiento",
            "descripcion": "Licencia especial clase F",
            "duracion_estimada": "35 minutos"
        },
        
        # PRIMER OTORGAMIENTO - PROFESIONALES
        {
            "id": "primer_otorg_clase_a1",
            "nombre": "Primer Otorgamiento - Clase A1 (Taxis)",
            "categoria": "primer_otorgamiento_profesional",
            "descripcion": "Licencia profesional para conducir taxis",
            "duracion_estimada": "60 minutos"
        },
        {
            "id": "primer_otorg_clase_a2",
            "nombre": "Primer Otorgamiento - Clase A2 (Transporte Medianos)",
            "categoria": "primer_otorgamiento_profesional",
            "descripcion": "Licencia para transporte de pasajeros medianos",
            "duracion_estimada": "60 minutos"
        },
        {
            "id": "primer_otorg_clase_a3",
            "nombre": "Primer Otorgamiento - Clase A3 (Buses)",
            "categoria": "primer_otorgamiento_profesional",
            "descripcion": "Licencia profesional para conducir buses",
            "duracion_estimada": "60 minutos"
        },
        {
            "id": "primer_otorg_clase_a4",
            "nombre": "Primer Otorgamiento - Clase A4 (Camiones Simples)",
            "categoria": "primer_otorgamiento_profesional",
            "descripcion": "Licencia para camiones de carga simples",
            "duracion_estimada": "60 minutos"
        },
        {
            "id": "primer_otorg_clase_a5",
            "nombre": "Primer Otorgamiento - Clase A5 (Camiones Articulados)",
            "categoria": "primer_otorgamiento_profesional",
            "descripcion": "Licencia para camiones articulados",
            "duracion_estimada": "60 minutos"
        },
        
        # RENOVACIÓN Y CONTROL
        {
            "id": "renovacion_licencia",
            "nombre": "Renovación de Licencia de Conducir",
            "categoria": "renovacion",
            "descripcion": "Renovación de licencia vigente o vencida",
            "duracion_estimada": "30 minutos"
        },
        {
            "id": "duplicado_licencia",
            "nombre": "Duplicado de Licencia",
            "categoria": "duplicado",
            "descripcion": "Solicitud de duplicado por pérdida o robo",
            "duracion_estimada": "20 minutos"
        },
        {
            "id": "canje_licencia_extranjera",
            "nombre": "Canje de Licencia Extranjera",
            "categoria": "canje",
            "descripcion": "Canje de licencia extranjera por chilena",
            "duracion_estimada": "40 minutos"
        },
        {
            "id": "licencia_diplomatico",
            "nombre": "Licencia de Diplomático",
            "categoria": "especial",
            "descripcion": "Licencia especial para personal diplomático",
            "duracion_estimada": "30 minutos"
        },
        {
            "id": "cambio_domicilio",
            "nombre": "Cambio de Domicilio",
            "categoria": "modificacion",
            "descripcion": "Actualización de domicilio en licencia",
            "duracion_estimada": "15 minutos"
        },
        {
            "id": "cambio_restriccion",
            "nombre": "Cambio de Restricción",
            "categoria": "modificacion",
            "descripcion": "Modificación de restricciones en licencia",
            "duracion_estimada": "20 minutos"
        },
        
        # OTROS TRÁMITES MUNICIPALES
        {
            "id": "permiso_circulacion",
            "nombre": "Permiso de Circulación",
            "descripcion": "Trámite de permiso de circulación vehicular",
            "categoria": "otros",
            "duracion_estimada": "15 minutos"
        },
        {
            "id": "certificado_residencia",
            "nombre": "Certificado de Residencia",
            "descripcion": "Certificado que acredita residencia en la comuna",
            "categoria": "otros",
            "duracion_estimada": "10 minutos"
        },
        {
            "id": "patente_comercial",
            "nombre": "Patente Comercial",
            "descripcion": "Solicitud o renovación de patente comercial",
            "categoria": "otros",
            "duracion_estimada": "45 minutos"
        },
        {
            "id": "permiso_edificacion",
            "nombre": "Permiso de Edificación",
            "descripcion": "Permisos para construcción y edificación",
            "categoria": "otros",
            "duracion_estimada": "60 minutos"
        },
        {
            "id": "registro_civil",
            "nombre": "Registro Civil",
            "descripcion": "Trámites de registro civil (certificados, matrimonio, etc.)",
            "categoria": "otros",
            "duracion_estimada": "20 minutos"
        },
        {
            "id": "subsidios",
            "nombre": "Subsidios Municipales",
            "descripcion": "Solicitud de subsidios y beneficios municipales",
            "categoria": "otros",
            "duracion_estimada": "40 minutos"
        },
        {
            "id": "otros",
            "nombre": "Otros Trámites",
            "descripcion": "Otros trámites municipales no especificados",
            "categoria": "otros",
            "duracion_estimada": "30 minutos"
        }
    ]
    return tipos_tramites

@app.post("/validar-requisitos-tramite")
async def validar_requisitos_tramite_endpoint(
    data: dict,
    current_user: dict = Depends(get_current_user)
):
    """
    🔍 RF05: Valida si un usuario cumple los requisitos para realizar un tipo de trámite.
    
    Consulta los datos municipales del usuario desde el servicio de autenticación
    y valida contra los requisitos configurados para el tipo de trámite.
    
    Body:
        {
            "tipo_tramite": "licencia_conducir",
            "user_id": 123  # Opcional, si no se envía usa current_user
        }
    
    Returns:
        {
            "puede_realizar": bool,
            "bloqueantes": [...],
            "advertencias": [...],
            "informativos": [...],
            "documentos_requeridos": [...]
        }
    """
    from requisitos_tramites import validar_requisitos_tramite
    
    tipo_tramite = data.get("tipo_tramite")
    user_id = data.get("user_id", current_user.get("user_id"))
    
    if not tipo_tramite:
        raise HTTPException(
            status_code=400,
            detail="Debe especificar el tipo de trámite"
        )
    
    try:
        # Consultar datos municipales del usuario desde el servicio de autenticación
        AUTH_SERVICE_URL = "http://auth-service-1:8000"
        
        async with httpx.AsyncClient() as client:
            # Obtener el token del header Authorization
            token = data.get("token")
            if not token:
                raise HTTPException(
                    status_code=401,
                    detail="Token de autenticación requerido"
                )
            
            response = await client.get(
                f"{AUTH_SERVICE_URL}/consultar-datos-municipales",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10.0
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Error al obtener datos municipales del usuario"
                )
            
            datos_response = response.json()
            datos_municipales = datos_response.get("datos_municipales", {})
        
        # Validar requisitos
        resultado = validar_requisitos_tramite(tipo_tramite, datos_municipales)
        
        logger.info(f"✅ Validación de requisitos para {tipo_tramite} - Usuario {user_id}: {resultado['puede_realizar']}")
        
        return {
            **resultado,
            "tipo_tramite": tipo_tramite,
            "user_id": user_id
        }
        
    except httpx.RequestError as e:
        logger.error(f"❌ Error conectando con servicio de autenticación: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="Error al conectar con el servicio de autenticación"
        )
    except Exception as e:
        logger.error(f"❌ Error validando requisitos: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al validar requisitos: {str(e)}"
        )

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