from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
import os, time

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://app:app@db:5432/contador")
engine = create_engine(DATABASE_URL, echo=True)

app = FastAPI(title="Contador API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # abierto para pruebas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

def wait_for_db():
    import traceback
    for i in range(30):  # más paciencia
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                print("✅ DB disponible")
                return
        except Exception as e:
            print(f"⏳ Esperando DB... intento {i+1}/30")
            traceback.print_exc()
            time.sleep(3)
    raise Exception("❌ No se pudo conectar a la base de datos")


wait_for_db()

@app.get("/contador")
def get_contador():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT valor FROM contador WHERE id=1")).scalar()
        return {"valor": result}

@app.post("/incrementar")
def incrementar():
    with engine.begin() as conn:
        conn.execute(text("UPDATE contador SET valor = valor + 1 WHERE id=1"))
        result = conn.execute(text("SELECT valor FROM contador WHERE id=1")).scalar()
        return {"valor": result}
