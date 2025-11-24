import psycopg
from passlib.context import CryptContext

# Crear contexto de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Generar hash para admin123
admin_hash = pwd_context.hash("admin123")

# Conectar a la base de datos
conn = psycopg.connect("postgresql://admin:admin@auth-db:5432/auth_db")
cur = conn.cursor()

# Actualizar la contraseña del admin
cur.execute(
    "UPDATE public.user SET hashed_password = %s WHERE email = %s",
    (admin_hash, "admin@municipalidad.cl")
)

conn.commit()

print(f"✅ Contraseña del admin actualizada correctamente")
print(f"   Email: admin@municipalidad.cl")
print(f"   Password: admin123")
print(f"   Hash: {admin_hash[:50]}...")

# Verificar
cur.execute("SELECT email, hashed_password FROM public.user WHERE email = 'admin@municipalidad.cl'")
result = cur.fetchone()
if result:
    email, stored_hash = result
    is_valid = pwd_context.verify("admin123", stored_hash)
    print(f"\n✓ Verificación: {'OK' if is_valid else 'FALLO'}")

cur.close()
conn.close()
