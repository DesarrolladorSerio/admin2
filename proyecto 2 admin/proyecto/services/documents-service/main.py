import json
import logging
import os
import uuid
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import List, Optional

from auth_utils import get_current_user
from db_documents import (
    buscar_documentos_antiguos,
    create_db_and_tables,
    create_documento_antiguo,
    create_documento_ciudadano,
    create_registro_digitalizacion,
    get_avance_digitalizacion_antigua,
    get_documentos_antiguos_pendientes,
    get_documentos_by_reserva,
    get_documentos_by_usuario,
    get_estadisticas_digitalizacion,
    get_registros_por_fecha,
    get_session,
    update_documento_antiguo,
    update_documento_estado,
)
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, status
from pydantic import BaseModel
from sqlmodel import Session

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI
app = FastAPI(
    title="Documents API",
    description="Servicio de gestión de documentos y digitalización",
    version="1.0.0"
)

# Configuración de almacenamiento
UPLOAD_DIR = Path("/app/storage/documents")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# =============================================================================
# MODELOS DE DATOS
# =============================================================================

class DocumentoCiudadanoCreate(BaseModel):
    reserva_id: int
    usuario_id: int
    usuario_rut: str
    tipo_documento: str
    nombre_archivo: str
    ruta_archivo: str
    tamano_bytes: int
    mime_type: str
    digitalizado_por: Optional[int] = None

class DocumentoAntiguoCreate(BaseModel):
    numero_expediente: str
    ciudadano_rut: Optional[str] = None
    ciudadano_nombre: Optional[str] = None
    tipo_tramite: str
    año_tramite: int
    descripcion: str
    numero_fojas: int = 1
    nombre_archivo: str
    ruta_archivo: str
    tamano_bytes: int
    digitalizado_por: Optional[int] = None
    palabras_clave: Optional[str] = None
    ubicacion_fisica: Optional[str] = None

class RegistroDigitalizacionCreate(BaseModel):
    fecha: date
    digitalizador_id: int
    digitalizador_nombre: str
    tipo_trabajo: str
    documentos_procesados: int
    paginas_digitalizadas: int
    tiempo_trabajado_minutos: int
    notas: Optional[str] = None

class DocumentoRevisionRequest(BaseModel):
    estado: str  # aprobado, rechazado
    notas: Optional[str] = None

class BusquedaDocumentosRequest(BaseModel):
    rut: Optional[str] = None
    nombre: Optional[str] = None
    expediente: Optional[str] = None
    año: Optional[int] = None
    tipo_tramite: Optional[str] = None
    skip: int = 0
    limit: int = 50

# =============================================================================
# EVENTOS
# =============================================================================

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    logger.info("✅ Base de datos de documentos inicializada")

# =============================================================================
# ENDPOINTS - DOCUMENTOS CIUDADANO (RF14-RF15)
# =============================================================================

@app.post("/upload-documento", status_code=status.HTTP_201_CREATED)
async def upload_documento(
    file: UploadFile = File(...),
    reserva_id: int = None,
    tipo_documento: str = None,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    RF14: Subir documento digitalizado (ciudadano con reserva)
    """
    try:
        # Generar nombre único
        file_extension = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = UPLOAD_DIR / unique_filename
        
        # Guardar archivo
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Crear registro en BD
        doc_data = DocumentoCiudadanoCreate(
            reserva_id=reserva_id,
            usuario_id=current_user["id"],
            usuario_rut=current_user.get("rut", ""),
            tipo_documento=tipo_documento,
            nombre_archivo=file.filename,
            ruta_archivo=str(file_path),
            tamano_bytes=len(content),
            mime_type=file.content_type or "application/octet-stream",
            digitalizado_por=current_user["id"]
        )
        
        documento = create_documento_ciudadano(session, doc_data)
        
        return {
            "success": True,
            "documento_id": documento.id,
            "message": "Documento subido exitosamente"
        }
    
    except Exception as e:
        logger.error(f"Error al subir documento: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/documentos/reserva/{reserva_id}")
def get_documentos_reserva(
    reserva_id: int,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Obtener documentos de una reserva"""
    documentos = get_documentos_by_reserva(session, reserva_id)
    return {"documentos": documentos}

@app.get("/documentos/usuario/{usuario_id}")
def get_documentos_usuario(
    usuario_id: int,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Obtener todos los documentos de un usuario"""
    # Verificar permisos
    if current_user["role"] not in ["admin", "employee"] and current_user["id"] != usuario_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No autorizado"
        )
    
    documentos = get_documentos_by_usuario(session, usuario_id)
    return {"documentos": documentos}

@app.put("/documentos/{documento_id}/revisar")
def revisar_documento(
    documento_id: int,
    revision: DocumentoRevisionRequest,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """RF08: Revisar documento (admin/employee)"""
    if current_user["role"] not in ["admin", "employee"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores y empleados pueden revisar documentos"
        )
    
    documento = update_documento_estado(
        session,
        documento_id,
        revision.estado,
        current_user["id"],
        revision.notas
    )
    
    if not documento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Documento no encontrado"
        )
    
    return {"success": True, "documento": documento}

# =============================================================================
# ENDPOINTS - DOCUMENTOS ANTIGUOS (RF15-RF16)
# =============================================================================

@app.post("/documentos-antiguos", status_code=status.HTTP_201_CREATED)
async def crear_documento_antiguo(
    file: UploadFile = File(...),
    numero_expediente: str = None,
    ciudadano_rut: Optional[str] = None,
    ciudadano_nombre: Optional[str] = None,
    tipo_tramite: str = None,
    año_tramite: int = None,
    descripcion: str = None,
    numero_fojas: int = 1,
    palabras_clave: Optional[str] = None,
    ubicacion_fisica: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    RF15: Digitalizar documento antiguo
    Solo digitalizadores y admins
    """
    if current_user["role"] not in ["admin", "digitalizador"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo digitalizadores pueden subir documentos antiguos"
        )
    
    try:
        # Generar nombre único
        file_extension = Path(file.filename).suffix
        unique_filename = f"antiguo_{año_tramite}_{uuid.uuid4()}{file_extension}"
        file_path = UPLOAD_DIR / "antiguos" / unique_filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Guardar archivo
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Crear registro
        doc_data = DocumentoAntiguoCreate(
            numero_expediente=numero_expediente,
            ciudadano_rut=ciudadano_rut,
            ciudadano_nombre=ciudadano_nombre,
            tipo_tramite=tipo_tramite,
            año_tramite=año_tramite,
            descripcion=descripcion,
            numero_fojas=numero_fojas,
            nombre_archivo=file.filename,
            ruta_archivo=str(file_path),
            tamano_bytes=len(content),
            digitalizado_por=current_user["id"],
            palabras_clave=palabras_clave,
            ubicacion_fisica=ubicacion_fisica
        )
        
        documento = create_documento_antiguo(session, doc_data)
        
        return {
            "success": True,
            "documento_id": documento.id,
            "message": "Documento antiguo digitalizado exitosamente"
        }
    
    except Exception as e:
        logger.error(f"Error al digitalizar documento antiguo: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/documentos-antiguos/pendientes")
def get_pendientes(
    limit: int = 50,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Obtener documentos antiguos pendientes de digitalizar"""
    if current_user["role"] not in ["admin", "digitalizador"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    documentos = get_documentos_antiguos_pendientes(session, limit)
    return {"documentos": documentos}

@app.post("/documentos-antiguos/buscar")
def buscar_antiguos(
    busqueda: BusquedaDocumentosRequest,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """RF16: Búsqueda de documentos antiguos catalogados"""
    if current_user["role"] not in ["admin", "employee", "digitalizador"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    documentos = buscar_documentos_antiguos(
        session,
        rut=busqueda.rut,
        nombre=busqueda.nombre,
        expediente=busqueda.expediente,
        año=busqueda.año,
        tipo_tramite=busqueda.tipo_tramite,
        skip=busqueda.skip,
        limit=busqueda.limit
    )
    
    return {"documentos": documentos, "count": len(documentos)}

@app.put("/documentos-antiguos/{doc_id}/completar")
def completar_digitalizacion_antigua(
    doc_id: int,
    calidad: str,  # baja, media, alta
    notas: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Marcar documento antiguo como completado"""
    if current_user["role"] not in ["admin", "digitalizador"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    documento = update_documento_antiguo(session, doc_id, {
        "estado_digitalizacion": "completado",
        "calidad_digitalizacion": calidad,
        "notas": notas,
        "fecha_digitalizacion": datetime.utcnow()
    })
    
    if not documento:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    return {"success": True, "documento": documento}

# =============================================================================
# ENDPOINTS - REGISTRO Y REPORTES (RF14, RF18)
# =============================================================================

@app.post("/registro-digitalizacion", status_code=status.HTTP_201_CREATED)
def crear_registro(
    registro: RegistroDigitalizacionCreate,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """RF14: Registrar jornada de digitalización"""
    if current_user["role"] not in ["admin", "digitalizador"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    registro_db = create_registro_digitalizacion(session, registro)
    return {"success": True, "registro": registro_db}

@app.get("/reportes/digitalizacion/diario")
def reporte_diario(
    fecha: date,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """RF18: Reporte diario de digitalización"""
    if current_user["role"] not in ["admin", "digitalizador"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    registros = get_registros_por_fecha(session, fecha, fecha)
    stats = get_estadisticas_digitalizacion(session, fecha, fecha)
    
    return {
        "fecha": fecha,
        "registros": registros,
        "estadisticas": stats
    }

@app.get("/reportes/digitalizacion/semanal")
def reporte_semanal(
    fecha_inicio: date,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """RF18: Reporte semanal de digitalización"""
    if current_user["role"] not in ["admin", "digitalizador"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    fecha_fin = fecha_inicio + timedelta(days=6)
    registros = get_registros_por_fecha(session, fecha_inicio, fecha_fin)
    stats = get_estadisticas_digitalizacion(session, fecha_inicio, fecha_fin)
    
    return {
        "periodo": f"{fecha_inicio} a {fecha_fin}",
        "registros": registros,
        "estadisticas": stats
    }

@app.get("/reportes/digitalizacion/mensual")
def reporte_mensual(
    año: int,
    mes: int,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """RF18: Reporte mensual de digitalización"""
    if current_user["role"] not in ["admin", "digitalizador"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    fecha_inicio = date(año, mes, 1)
    # Último día del mes
    if mes == 12:
        fecha_fin = date(año, 12, 31)
    else:
        fecha_fin = date(año, mes + 1, 1) - timedelta(days=1)
    
    registros = get_registros_por_fecha(session, fecha_inicio, fecha_fin)
    stats = get_estadisticas_digitalizacion(session, fecha_inicio, fecha_fin)
    
    return {
        "periodo": f"{fecha_inicio.strftime('%B %Y')}",
        "registros": registros,
        "estadisticas": stats
    }

@app.get("/reportes/avance-antiguos")
def reporte_avance_antiguos(
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """RF18: Avance general de digitalización de documentos antiguos"""
    if current_user["role"] not in ["admin", "digitalizador"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    avance = get_avance_digitalizacion_antigua(session)
    return {
        "avance": avance,
        "meta_total": 100000,
        "meta_alcanzada_porcentaje": (avance["completados"] / 100000 * 100) if avance["completados"] else 0
    }

# =============================================================================
# HEALTH CHECK
# =============================================================================

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "documents"}
