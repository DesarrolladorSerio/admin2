from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash del admin en la BD
stored_hash = "$2b$12$MJIbv3CURAqZTL0YM3PJc.qJJiMlxmllxjZwQccTH1tM9U/lXe2wm"

# Probar con admin123
print("Probando 'admin123':", pwd_context.verify("admin123", stored_hash))

# Generar un nuevo hash para admin123
new_hash = pwd_context.hash("admin123")
print(f"\nNuevo hash para 'admin123': {new_hash}")
print("Verificando nuevo hash:", pwd_context.verify("admin123", new_hash))
