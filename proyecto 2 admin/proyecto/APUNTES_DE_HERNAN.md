# 📝 APUNTES DE HERNÁN - GUÍA RÁPIDA DEL PROYECTO

> **Para Bruno (IA)**: Lee este archivo completo para entender el contexto del proyecto y qué falta por hacer.
> **Para Hernán**: Usa esta guía para desarrollar componentes y solucionar problemas.

---

## 🎯 CONTEXTO DEL PROYECTO

**Proyecto**: Sistema de Reserva de Horas para Licencias de Conducir - Municipalidad de Linares  
**Licitación**: 2337-58-LP25  
**Estado actual**: 78% completo  
**Stack**: FastAPI + SQLModel + React + Nginx + Docker

---

## 🏗️ ARQUITECTURA DEL SISTEMA

### Flujo de Comunicación: Backend → Nginx → Frontend

```
[Frontend React]
      ↓ HTTP Request (puerto 80)
[Nginx API Gateway] ← Maneja CORS, Load Balancing, Routing
      ↓ Proxy Pass
[Microservicios Backend]
      ↓
[PostgreSQL]
```

**⚠️ IMPORTANTE**: 
- **NO crear middlewares CORS en FastAPI** - Nginx lo maneja todo
- **NO agregar CORS en backend** - Ya está configurado en nginx.conf
- Todos los servicios backend responden en puerto interno (8000, 8002, etc)
- El frontend hace peticiones a `http://localhost/api/...`
- Nginx redirige al servicio correcto

### Servicios Existentes

1. **auth-service** (puerto 8000) - Autenticación, usuarios, datos municipales
2. **reservations-service** (puerto 8002) - Reservas, calendario, disponibilidad
3. **documents-service** (puerto 8003) - Documentos, digitalización
4. **notifications-service** (puerto 8004) - Emails, notificaciones
5. **chatbot-service** (puerto 8005) - IA con Ollama
6. **api-gateway** (puerto 80) - Nginx (enrutamiento)
7. **frontend** (puerto 5173) - React + Vite

---

## 📚 PASO 1: CREAR UN NUEVO COMPONENTE/SERVICIO

### A) Crear la Base de Datos con SQLModel

**Archivo**: `db_nombre_servicio.py`

```python
from sqlmodel import Field, Session, SQLModel, create_engine, select
from datetime import datetime
import os

# 1. Configurar conexión
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:admin@db:5432/proyecto_db")
engine = create_engine(DATABASE_URL)

# 2. Definir el modelo (tabla)
class MiTabla(SQLModel, table=True):
    """Descripción de la tabla"""
    __tablename__ = "mi_tabla"  # Nombre explícito de la tabla
    
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")  # FK si es necesaria
    nombre: str = Field(index=True)  # Indexado para búsquedas rápidas
    email: str | None = Field(default=None)  # Campo opcional
    estado: str = Field(default="activo")
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow)
    fecha_modificacion: datetime | None = Field(default=None)

# 3. Crear tablas
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# 4. Función para obtener sesiones
def get_session():
    with Session(engine) as session:
        yield session
```

**Tipos de datos SQLModel**:
- `str` - Texto
- `int` - Enteros
- `float` - Decimales
- `bool` - Verdadero/Falso
- `datetime` - Fechas
- `str | None` - Opcional (puede ser NULL)

### B) Crear el Servicio FastAPI

**Archivo**: `main.py`

```python
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select
from db_nombre_servicio import MiTabla, create_db_and_tables, get_session
from pydantic import BaseModel
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear app FastAPI SIN middlewares CORS (Nginx lo maneja)
app = FastAPI(title="Mi Servicio", version="1.0.0")

# Modelos Pydantic para request/response
class MiRequest(BaseModel):
    nombre: str
    email: str

class MiResponse(BaseModel):
    id: int
    nombre: str
    email: str
    estado: str

# Inicializar BD al arrancar
@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    logger.info("✅ Base de datos inicializada")

# Endpoints
@app.get("/health")
def health_check():
    return {"status": "ok", "service": "mi-servicio"}

@app.post("/api/mi-servicio/crear", response_model=MiResponse)
def crear_item(request: MiRequest, session: Session = Depends(get_session)):
    """Crear un nuevo item"""
    try:
        nuevo_item = MiTabla(
            nombre=request.nombre,
            email=request.email
        )
        session.add(nuevo_item)
        session.commit()
        session.refresh(nuevo_item)
        
        logger.info(f"✅ Item creado: {nuevo_item.id}")
        return nuevo_item
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/mi-servicio/listar")
def listar_items(session: Session = Depends(get_session)):
    """Listar todos los items"""
    statement = select(MiTabla)
    items = session.exec(statement).all()
    return {"items": items, "total": len(items)}

@app.get("/api/mi-servicio/{item_id}")
def obtener_item(item_id: int, session: Session = Depends(get_session)):
    """Obtener un item por ID"""
    item = session.get(MiTabla, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    return item

@app.put("/api/mi-servicio/{item_id}")
def actualizar_item(item_id: int, request: MiRequest, session: Session = Depends(get_session)):
    """Actualizar un item"""
    item = session.get(MiTabla, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    
    item.nombre = request.nombre
    item.email = request.email
    session.add(item)
    session.commit()
    session.refresh(item)
    return item

@app.delete("/api/mi-servicio/{item_id}")
def eliminar_item(item_id: int, session: Session = Depends(get_session)):
    """Eliminar un item"""
    item = session.get(MiTabla, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    
    session.delete(item)
    session.commit()
    return {"message": "Item eliminado", "id": item_id}
```

### C) Configurar Nginx para el nuevo servicio

**Archivo**: `services/api-gateway/nginx.conf`

Agregar al archivo:

```nginx
# Upstream para el nuevo servicio
upstream mi_servicio_cluster {
    server mi-servicio:8006;  # Puerto del nuevo servicio
}

# Dentro del bloque server {}
location /api/mi-servicio/ {
    proxy_pass http://mi_servicio_cluster;
    proxy_http_version 1.1;
    proxy_set_header Connection "";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}
```

### D) Agregar al docker-compose.yml

```yaml
  mi-servicio:
    build: ./services/mi-servicio
    container_name: mi_servicio
    ports:
      - "8006:8006"
    environment:
      - DATABASE_URL=postgresql://admin:admin@db:5432/proyecto_db
    depends_on:
      - db
    networks:
      - proyecto_network
    restart: unless-stopped
```

---

## 🔐 AUTENTICACIÓN Y AUTORIZACIÓN

### Cómo funciona el sistema de autenticación

1. **Usuario se registra/logea** → `POST /api/auth/login`
2. **Backend genera JWT token** → Contiene: user_id, email, role
3. **Frontend guarda token** → localStorage o sessionStorage
4. **Peticiones protegidas** → Header: `Authorization: Bearer <token>`
5. **Backend valida token** → Extrae user_id y role

### Ejemplo: Endpoint protegido

```python
from fastapi import Header, HTTPException
from jose import jwt, JWTError

SECRET_KEY = "un-secreto-muy-fuerte-y-largo"
ALGORITHM = "HS256"

def verify_token(authorization: str = Header(None)):
    """Verifica el token JWT del header"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Token no proporcionado")
    
    try:
        token = authorization.replace("Bearer ", "")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload  # Contiene user_id, email, role
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

@app.get("/api/mi-servicio/protegido")
def endpoint_protegido(user_data = Depends(verify_token)):
    """Solo accesible con token válido"""
    return {
        "message": "Acceso concedido",
        "user_id": user_data.get("sub"),
        "role": user_data.get("role")
    }
```

---

## 📋 REQUISITOS FALTANTES (Del Informe de Licitación)

### ⚠️ PRIORIDAD ALTA - Faltan Componentes Frontend

#### 1. **RF11: Reportes PDF y Excel** (6-8 horas)
- **Estado**: Solo CSV implementado
- **Falta**:
  - Generación de PDF con `jspdf` o `react-pdf`
  - Exportación Excel con `xlsx`
  - Gráficos con `recharts` o `chart.js`
- **Archivos**: 
  - Backend: `/api/reservations/admin/estadisticas-tramites` ✅
  - Frontend: Crear `ReportesExportacion.jsx` ❌

#### 2. **RF14-RF18: Módulo Digitalizador** (12-16 horas)
- **Estado**: Backend 100%, Frontend 0%
- **Falta**:
  - `SubirDocumento.jsx` - Interfaz para subir docs escaneados
  - `Catalogacion.jsx` - Búsqueda avanzada de documentos
  - `ReportesDigitalizacion.jsx` - Dashboard con gráficos
- **APIs disponibles**:
  - `POST /api/documents/ciudadano/subir` ✅
  - `POST /api/documents/antiguos/subir` ✅
  - `GET /api/documents/antiguos/buscar` ✅
  - `GET /api/documents/reportes/diario` ✅
  - `GET /api/documents/reportes/avance-general` ✅

### ✅ Lo que SÍ está completo

- Autenticación con RUT ✅
- Reservas de horas ✅
- Calendario ✅
- Subida de documentos ciudadanos ✅
- Notificaciones por email ✅
- Dashboard administrativo ✅
- Búsquedas avanzadas ✅
- Chatbot con IA ✅
- Vencimientos de licencias ✅

---

## 🐛 GUÍA DE DEBUGGING - PARA HERNÁN

### Si algo no funciona, sigue estos pasos:

### 1. **Ver logs del contenedor Docker**

```powershell
# Ver logs de un servicio específico
docker logs nombre_contenedor --tail=50

# Ejemplos:
docker logs auth_service_1 --tail=50
docker logs reservations_service_1 --tail=50
docker logs documents_service --tail=50
docker logs frontend --tail=50

# Ver logs en tiempo real
docker logs -f nombre_contenedor
```

### 2. **Verificar que el contenedor está corriendo**

```powershell
# Ver todos los contenedores
docker ps

# Ver incluso los que están parados
docker ps -a

# Reiniciar un servicio
docker restart nombre_contenedor

# Reiniciar todo
docker compose restart
```

### 3. **Ver logs del navegador (F12)**

1. Abre el navegador (Chrome/Edge/Firefox)
2. Presiona **F12** o **Ctrl+Shift+I**
3. Ve a la pestaña **Console**
4. Busca errores en rojo 🔴
5. **Copia el texto completo del error** y pásaselo a Bruno (IA)

**Ejemplo de error común**:
```
❌ Failed to fetch
❌ CORS error
❌ 404 Not Found
❌ 500 Internal Server Error
```

### 4. **Ver peticiones de red (F12 → Network)**

1. Presiona **F12**
2. Ve a **Network** (o **Red**)
3. Recarga la página (F5)
4. Haz clic en la petición que falló (en rojo)
5. Ve a **Headers** → Copia la URL
6. Ve a **Response** → Copia la respuesta del servidor
7. **Pásale todo esto a Bruno (IA)**

### 5. **Verificar conexión a la base de datos**

```powershell
# Entrar al contenedor de PostgreSQL
docker exec -it postgres_db psql -U admin -d proyecto_db

# Ver todas las tablas
\dt

# Ver datos de una tabla
SELECT * FROM "user" LIMIT 5;
SELECT * FROM reservation LIMIT 5;

# Salir
\q
```

### 6. **Errores comunes y soluciones**

| Error | Causa | Solución |
|-------|-------|----------|
| `CORS error` | Nginx no está corriendo | `docker restart api-gateway` |
| `404 Not Found` | Ruta incorrecta o servicio caído | Verificar nginx.conf y docker ps |
| `500 Internal Error` | Error en backend | Ver logs del servicio con `docker logs` |
| `Connection refused` | Servicio no está escuchando | Verificar puerto en docker-compose.yml |
| `Database error` | PostgreSQL no disponible | `docker restart postgres_db` |
| `Token inválido` | JWT expirado o mal formado | Volver a hacer login |

---

## 📝 EJEMPLOS DE USO - PARA PASARLE A BRUNO

### Ejemplo 1: "Bruno, el login no funciona"

```
Hernán: Bruno, el login no funciona. Aquí están los logs:

Terminal:
docker logs auth_service_1 --tail=50
[Error en línea 145: connection refused to database]

Console (F12):
POST http://localhost/api/auth/login 500 (Internal Server Error)
Response: {"detail": "Database connection failed"}

¿Qué hago?
```

### Ejemplo 2: "Bruno, necesito crear un servicio de reportes"

```
Hernán: Bruno, necesito crear un servicio para generar reportes en PDF.
Debe tener:
- Tabla "reportes" con: id, user_id, tipo, fecha, estado
- Endpoint POST /api/reportes/generar
- Endpoint GET /api/reportes/listar
- Usar FastAPI y SQLModel

Lee APUNTES_DE_HERNAN.md y ayúdame a crearlo.
```

### Ejemplo 3: "Bruno, hay un error en el frontend"

```
Hernán: Bruno, el componente de documentos da error. Logs del navegador:

Console:
Uncaught TypeError: Cannot read property 'map' of undefined
  at DocumentList.jsx:45

Network:
GET http://localhost/api/documents/listar 200 OK
Response: {"documents": null, "total": 0}

El problema es que 'documents' viene null en lugar de array vacío.
¿Cómo lo arreglo?
```

---

## 🔧 COMANDOS ÚTILES PARA HERNÁN

### Docker

```powershell
# Ver logs de todos los servicios
docker compose logs

# Reconstruir y levantar todo
docker compose up -d --build

# Parar todo
docker compose down

# Parar y eliminar volúmenes (⚠️ borra datos)
docker compose down -v

# Ver uso de recursos
docker stats
```

### Desarrollo

```powershell
# Instalar dependencias Python
pip install fastapi sqlmodel uvicorn psycopg2-binary

# Correr servicio localmente (fuera de Docker)
cd services/mi-servicio
uvicorn main:app --reload --port 8000

# Instalar dependencias React
cd services/frontend
npm install
npm run dev
```

### Base de datos

```powershell
# Backup de la base de datos
docker exec postgres_db pg_dump -U admin proyecto_db > backup.sql

# Restaurar backup
docker exec -i postgres_db psql -U admin proyecto_db < backup.sql
```

---

## 📞 COMUNICACIÓN CON BRUNO (IA)

### Cómo pedirle ayuda a Bruno:

1. **Sé específico**: No digas "no funciona", di "el endpoint X retorna error Y"
2. **Pega los logs completos**: Copia y pega todo el error
3. **Menciona este archivo**: "Bruno, lee APUNTES_DE_HERNAN.md"
4. **Pega el código relevante**: Si modificaste algo, muéstralo
5. **Pega la respuesta del servidor**: F12 → Network → Response

### Ejemplos de buenas peticiones:

✅ **BIEN**: 
```
Bruno, lee APUNTES_DE_HERNAN.md. Necesito crear el endpoint para 
generar reportes PDF. Debe usar SQLModel y conectarse a la BD existente.
```

✅ **BIEN**: 
```
Bruno, el servicio de documentos da este error:
[pego logs completos]
¿Qué está mal?
```

❌ **MAL**: 
```
Bruno, ayuda, no funciona nada
```

❌ **MAL**: 
```
Bruno, crea un reporte
```

---

## 🎨 ESTRUCTURA DE COMPONENTE REACT (Frontend)

```jsx
import { useState, useEffect } from 'react';
import axios from 'axios';

function MiComponente() {
  const [datos, setDatos] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Obtener datos al cargar
  useEffect(() => {
    cargarDatos();
  }, []);

  const cargarDatos = async () => {
    setLoading(true);
    try {
      // Token de autenticación
      const token = localStorage.getItem('token');
      
      const response = await axios.get('/api/mi-servicio/listar', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      setDatos(response.data.items);
      console.log('✅ Datos cargados:', response.data);
    } catch (err) {
      console.error('❌ Error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const crearItem = async (nombre, email) => {
    try {
      const token = localStorage.getItem('token');
      
      const response = await axios.post('/api/mi-servicio/crear', 
        { nombre, email },
        { headers: { 'Authorization': `Bearer ${token}` } }
      );
      
      console.log('✅ Item creado:', response.data);
      cargarDatos(); // Recargar lista
    } catch (err) {
      console.error('❌ Error al crear:', err);
      alert('Error: ' + err.response?.data?.detail);
    }
  };

  if (loading) return <div>Cargando...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Mi Componente</h1>
      
      <div className="grid gap-4">
        {datos.map(item => (
          <div key={item.id} className="border p-4 rounded">
            <h2>{item.nombre}</h2>
            <p>{item.email}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default MiComponente;
```

---

## 📊 RESUMEN EJECUTIVO

### Estado Actual: 78% Completo

**✅ Completo (Backend + Frontend)**:
- Sistema de autenticación y usuarios
- Reservas de horas con calendario
- Subida de documentos ciudadanos
- Notificaciones por email
- Dashboard administrativo
- Búsquedas avanzadas
- Chatbot con IA
- Gestión de vencimientos

**⚠️ Backend completo, falta Frontend**:
- Módulo de digitalización (RF14-RF18)
- Reportes con gráficos

**❌ Por implementar**:
- Generación de PDF
- Exportación a Excel
- Componentes de digitalización

---

## 🚀 PRÓXIMOS PASOS

1. **Implementar componentes de digitalización** (Prioridad Alta)
   - `SubirDocumento.jsx`
   - `Catalogacion.jsx`
   - `ReportesDigitalizacion.jsx`

2. **Agregar exportación PDF/Excel** (Prioridad Media)
   - Instalar `jspdf` y `xlsx`
   - Modificar `BusquedaAvanzada.jsx`

3. **Testing completo del sistema** (Prioridad Alta)
   - Probar todos los flujos
   - Verificar integración frontend-backend

---

## 💡 TIPS FINALES

1. **Siempre revisa los logs** antes de preguntar
2. **Usa console.log()** en frontend para debug
3. **Usa logger.info()** en backend para debug
4. **No modifiques nginx.conf** sin entender el flujo
5. **No agregues CORS** en FastAPI (ya está en Nginx)
6. **Commitea frecuentemente** en Git
7. **Documenta los cambios** que hagas
8. **Pregúntale a Bruno** con contexto completo

---

**Fin de los apuntes. ¡Éxito Hernán! 🚀**

*Última actualización: 10 de noviembre de 2025*
