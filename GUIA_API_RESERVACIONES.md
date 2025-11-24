# 📋 Guía Completa: API de Reservaciones paso a paso

## 🎯 Objetivo
Crear un servicio de reservaciones completo que permita:
- Gestionar usuarios y reservaciones en base de datos
- API REST con endpoints CRUD
- Integración con calendario frontend
- Comunicación segura entre microservicios

---

## 📁 Estructura del Proyecto

```
services/reservations-service/
├── main.py              # API FastAPI principal
├── db_reservas.py       # Modelos y funciones de base de datos  
├── requirements.txt     # Dependencias Python
└── Dockerfile          # Configuración Docker
```

---

## 🔧 Paso 1: Configurar Base de Datos (db_reservas.py)

### ¿Qué hace este archivo?
- Define modelos de datos con SQLModel (ORM)
- Conecta a PostgreSQL usando variables de entorno
- Proporciona funciones para CRUD de usuarios y reservaciones

### Código completo:

```python
from sqlmodel import SQLModel, Field, Session, create_engine, select
from datetime import datetime, date, time
from typing import Optional
import os

# =============================================================================
# CONFIGURACIÓN DE BASE DE DATOS
# =============================================================================

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:admin@reservations-db:5432/reservations_db")
engine = create_engine(DATABASE_URL)

# =============================================================================
# MODELOS DE BASE DE DATOS
# =============================================================================

class User(SQLModel, table=True):
    """Modelo de usuario - compartido con auth-service"""
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    hashed_password: str

class Reservation(SQLModel, table=True):
    """Modelo de reservación"""
    id: int | None = Field(default=None, primary_key=True)
    fecha: date = Field(description="Fecha de la reservación")
    hora: time = Field(description="Hora de la reservación")
    usuario_id: int = Field(foreign_key="user.id", description="ID del usuario que reserva")
    usuario_nombre: str = Field(description="Nombre del usuario (cache)")
    descripcion: str = Field(default="", description="Descripción de la reservación")
    estado: str = Field(default="activa", description="Estado: activa, cancelada, completada")
    created_at: datetime = Field(default_factory=datetime.utcnow)

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

def get_all_users(session: Session) -> list[User]:
    """Obtiene todos los usuarios."""
    statement = select(User)
    return session.exec(statement).all()

def get_user_by_id(session: Session, user_id: int) -> User | None:
    """Busca un usuario por ID."""
    statement = select(User).where(User.id == user_id)
    return session.exec(statement).first()

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
```

### ¿Por qué cada función?
- **`create_db_and_tables()`**: Inicializa las tablas al arrancar el servicio
- **`get_session()`**: Maneja conexiones de base de datos de forma segura
- **`get_all_users()`**: Para mostrar lista de usuarios en el frontend
- **CRUD de reservaciones**: Crear, leer, actualizar, eliminar reservaciones
- **`get_reservations_by_date_range()`**: Específico para mostrar calendario mensual

---

## 🚀 Paso 2: API REST Principal (main.py)

### ¿Qué hace este archivo?
- Define endpoints HTTP para la API
- Valida datos con Pydantic
- Maneja errores y respuestas JSON
- Conecta con la base de datos

### Código completo:

```python
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
    User
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
def get_users(session: Session = Depends(get_session)):
    """Obtiene la lista de todos los usuarios."""
    users = get_all_users(session)
    return [UserResponse(id=user.id, username=user.username) for user in users]

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, session: Session = Depends(get_session)):
    """Obtiene un usuario específico por ID."""
    user = get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return UserResponse(id=user.id, username=user.username)

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
```

### ¿Por qué cada endpoint?
- **`GET /users`**: Para llenar dropdown de usuarios en el frontend
- **`GET /reservations`**: Lista completa para administración  
- **`POST /reservations`**: Crear nueva reservación desde formulario
- **`PUT /reservations/{id}`**: Editar reservación existente
- **`DELETE /reservations/{id}`**: Cancelar/eliminar reservación
- **`GET /reservations/calendar/{start}/{end}`**: Datos específicos para calendario mensual

---

## 🔧 Paso 3: Configurar Gateway (nginx.conf)

### ¿Qué hace?
- Enruta peticiones entre frontend y servicios backend
- Maneja CORS y headers de proxy
- Proporciona URLs limpias para el frontend

### Código:

```nginx
http {
    upstream backend_cluster {
        server auth-service:8000;
    }

    upstream reservations_cluster {
        server reservations-service:8000;
    }

    upstream frontend_app {
        server proyecto_frontend:80;
    }

    server {
        listen 80;
        server_name proyecto-redes.local;

        # 🔹 Rutas de autenticación
        location /api/auth/ {
            rewrite ^/api/auth(/.*)$ $1 break;
            proxy_pass http://backend_cluster;
            proxy_http_version 1.1;
            proxy_set_header Connection "";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # 🔹 Rutas de reservaciones  
        location /api/reservations/ {
            rewrite ^/api/reservations(/.*)$ $1 break;
            proxy_pass http://reservations_cluster;
            proxy_http_version 1.1;
            proxy_set_header Connection "";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # 🔹 Backward compatibility para login/register
        location /api/token {
            proxy_pass http://backend_cluster/token;
            proxy_http_version 1.1;
            proxy_set_header Connection "";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /api/register {
            proxy_pass http://backend_cluster/register;
            proxy_http_version 1.1;
            proxy_set_header Connection "";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # 🔹 Rutas frontend
        location / {
            proxy_pass http://frontend_app;
            proxy_http_version 1.1;
            proxy_set_header Connection "";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # 🔹 Healthcheck del gateway
        location /health {
            access_log off;
            return 200 "Gateway OK";
        }
    }
}
```

### ¿Por qué estas rutas?
- **`/api/reservations/*`**: Todo lo relacionado con reservaciones va al reservations-service
- **`/api/token` y `/api/register`**: Mantiene compatibilidad con el login existente
- **`/`**: Frontend React servido por Nginx

---

## 🐳 Paso 4: Ejecutar con Docker

### Comando:
```bash
docker compose up -d --build
```

### ¿Qué pasa?
1. Se construyen las imágenes de cada servicio
2. Se levantan las bases de datos PostgreSQL
3. Se inician los servicios backend (auth + reservations)
4. Se construye y sirve el frontend
5. Se configura el gateway como punto de entrada

---

## 📡 Paso 5: Probar la API

### URLs principales:
- **Frontend**: `http://localhost:8080`
- **API Reservaciones**: `http://localhost:8080/api/reservations/`
- **API Autenticación**: `http://localhost:8080/api/token`

### Ejemplos de peticiones:

#### 1. Obtener usuarios:
```bash
curl http://localhost:8080/api/reservations/users
```

#### 2. Crear reservación:
```bash
curl -X POST http://localhost:8080/api/reservations/reservations \
  -H "Content-Type: application/json" \
  -d '{
    "fecha": "2025-11-10",
    "hora": "14:30:00", 
    "usuario_id": 1,
    "usuario_nombre": "admin@municipalidad.cl",
    "descripcion": "Reunión importante"
  }'
```

#### 3. Obtener reservaciones del mes:
```bash
curl http://localhost:8080/api/reservations/reservations/calendar/2025-11-01/2025-11-30
```

---

## 🎨 Paso 6: Integrar con Frontend React

### En tu componente Reservas.jsx:

```javascript
import React, { useState, useEffect } from 'react';
import axios from 'axios';

export default function Reservas() {
    const [reservations, setReservations] = useState([]);
    const [users, setUsers] = useState([]);

    useEffect(() => {
        // Cargar usuarios y reservaciones al montar
        loadUsers();
        loadReservations();
    }, []);

    const loadUsers = async () => {
        try {
            const response = await axios.get('/api/reservations/users');
            setUsers(response.data);
        } catch (error) {
            console.error('Error loading users:', error);
        }
    };

    const loadReservations = async () => {
        try {
            const response = await axios.get('/api/reservations/reservations');
            setReservations(response.data);
        } catch (error) {
            console.error('Error loading reservations:', error);
        }
    };

    const createReservation = async (reservationData) => {
        try {
            await axios.post('/api/reservations/reservations', reservationData);
            loadReservations(); // Recargar lista
        } catch (error) {
            console.error('Error creating reservation:', error);
        }
    };

    return (
        <div>
            <h1>Reservaciones</h1>
            {/* Aquí irían tus componentes de calendario/formulario */}
        </div>
    );
}
```

---

## 🔍 Debugging y Logs

### Ver logs de servicios:
```bash
# Logs de reservations-service
docker compose logs reservations-service

# Logs de todos los servicios
docker compose logs -f
```

### Verificar estado:
```bash
# Ver contenedores corriendo
docker compose ps

# Healthchecks
curl http://localhost:8080/health
curl http://localhost:8080/api/reservations/health
```

---

## 🎯 Resumen de Flujo Completo

1. **Usuario hace login** → Auth-service valida y devuelve token
2. **Usuario va a reservas** → Frontend carga `/api/reservations/users`  
3. **Usuario crea reservación** → POST a `/api/reservations/reservations`
4. **Frontend muestra calendario** → GET a `/api/reservations/reservations/calendar/{mes}`
5. **Usuario edita/elimina** → PUT/DELETE a `/api/reservations/reservations/{id}`

### 🔗 URLs de Producción:
- **Frontend**: `http://localhost:8080/`
- **Login**: `http://localhost:8080/login`
- **Reservas**: `http://localhost:8080/reservas`
- **API Docs**: `http://localhost:8080/api/reservations/docs`

---

## ✅ Checklist de Implementación

- [ ] Crear `db_reservas.py` con modelos y funciones
- [ ] Crear `main.py` con API REST completa
- [ ] Actualizar `nginx.conf` con rutas de reservaciones
- [ ] Ejecutar `docker compose up -d --build`
- [ ] Probar endpoints con curl o Postman
- [ ] Integrar frontend React con axios
- [ ] Implementar calendario (opcional)

¡Con esto tienes una API de reservaciones completa y funcional! 🚀