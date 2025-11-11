import requests
import json
import random
from datetime import datetime, timedelta

# --- Configuración ---
BASE_URL = "http://localhost"
ADMIN_EMAIL = "admin@municipalidad.cl"
ADMIN_PASSWORD = "admin123"
NUM_USERS_TO_CREATE = 10
RESERVATIONS_PER_USER = 3

# --- Funciones Auxiliares ---
def generate_random_rut():
    """Genera un RUT chileno aleatorio válido (sin puntos, con guion y dígito verificador)."""
    rut_base = random.randint(1_000_000, 25_000_000)
    s = str(rut_base)
    reversed_digits = list(map(int, s[::-1]))
    factor = 2
    sum_digits = 0
    for digit in reversed_digits:
        sum_digits += digit * factor
        factor = factor + 1 if factor < 7 else 2
    dv = 11 - (sum_digits % 11)
    if dv == 11:
        dv = '0'
    elif dv == 10:
        dv = 'K'
    else:
        dv = str(dv)
    return f"{rut_base}-{dv}"

def generate_random_name():
    first_names = ["Juan", "María", "Pedro", "Ana", "Luis", "Sofía", "Carlos", "Laura"]
    last_names = ["Pérez", "González", "Rodríguez", "Díaz", "Sánchez", "Martínez", "Torres", "Flores"]
    return f"{random.choice(first_names)} {random.choice(last_names)}"

def generate_random_email(name):
    return f"{name.lower().replace(' ', '.')}{random.randint(1, 100)}@example.com"

def generate_random_password():
    return "password123" # Contraseña simple para usuarios de prueba

def get_random_future_date():
    today = datetime.now()
    future_date = today + timedelta(days=random.randint(1, 365))
    return future_date.strftime("%Y-%m-%d")

def get_random_time():
    hour = random.randint(9, 17) # Horario de 9 AM a 5 PM
    minute = random.choice([0, 30])
    return f"{hour:02d}:{minute:02d}"

# --- Main Script ---
def main():
    print("--- Generando Datos de Prueba ---")

    # 1. Login de Admin para obtener token
    print("\n1. Iniciando sesión como administrador...")
    admin_token = None
    try:
        login_payload = {
            "identifier": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD,
            "login_type": "email"
        }
        response = requests.post(f"{BASE_URL}/api/auth/token", json=login_payload)
        response.raise_for_status()
        admin_token = response.json()["access_token"]
        print("   ✅ Token de administrador obtenido.")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error al iniciar sesión como administrador: {e}")
        return

    headers = {"Authorization": f"Bearer {admin_token}"}

    # 2. Obtener tipos de trámites disponibles
    print("\n2. Obteniendo tipos de trámites disponibles...")
    tipos_tramites = []
    try:
        response = requests.get(f"{BASE_URL}/api/reservations/tipos-tramites", headers=headers)
        response.raise_for_status()
        tipos_tramites = [t["nombre"] for t in response.json()]
        print(f"   ✅ Tipos de trámites obtenidos: {', '.join(tipos_tramites)}")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error al obtener tipos de trámites: {e}")
        return

    if not tipos_tramites:
        print("   ⚠️ No se encontraron tipos de trámites. No se pueden crear reservas.")
        return

    # 3. Generar Usuarios y Reservas
    print(f"\n3. Creando {NUM_USERS_TO_CREATE} usuarios y {RESERVATIONS_PER_USER} reservas por usuario...")
    created_users = []
    for i in range(NUM_USERS_TO_CREATE):
        name = generate_random_name()
        email = generate_random_email(name)
        password = generate_random_password()
        rut = generate_random_rut()

        user_data = {
            "email": email,
            "password": password,
            "nombre": name,
            "rut": rut,
            "role": "user" # Todos los usuarios de prueba serán 'user'
        }

        print(f"\n   Creando usuario {i+1}/{NUM_USERS_TO_CREATE}: {name} ({email})...")
        try:
            # El endpoint de registro no requiere token de admin
            register_response = requests.post(f"{BASE_URL}/api/auth/register", json=user_data)
            register_response.raise_for_status()
            user_id = register_response.json().get("id")
            created_users.append({"id": user_id, "email": email, "password": password, "name": name})
            print(f"      ✅ Usuario creado (ID: {user_id}).")

            # Login del nuevo usuario para obtener su token
            user_token = None
            try:
                user_login_payload = {
                    "identifier": email,
                    "password": password,
                    "login_type": "email"
                }
                user_login_response = requests.post(f"{BASE_URL}/api/auth/token", json=user_login_payload)
                user_login_response.raise_for_status()
                user_token = user_login_response.json()["access_token"]
                user_headers = {"Authorization": f"Bearer {user_token}"}
                print(f"      ✅ Token para {name} obtenido.")
            except requests.exceptions.RequestException as e:
                print(f"      ❌ Error al obtener token para {name}: {e}")
                continue # No podemos crear reservas sin token

            # Crear reservas para este usuario
            for j in range(RESERVATIONS_PER_USER):
                fecha = get_random_future_date()
                hora = get_random_time()
                tipo_tramite = random.choice(tipos_tramites)
                
                reservation_data = {
                    "fecha": fecha,
                    "hora": hora,
                    "tipo_tramite": tipo_tramite,
                    "descripcion": f"Reserva de prueba para {name} - {tipo_tramite}"
                }
                print(f"         Creando reserva {j+1}/{RESERVATIONS_PER_USER} para {name} ({tipo_tramite} el {fecha} a las {hora})...")
                try:
                    reservation_response = requests.post(f"{BASE_URL}/api/reservations/reservations", json=reservation_data, headers=user_headers)
                    reservation_response.raise_for_status()
                    print(f"            ✅ Reserva creada (ID: {reservation_response.json().get('id')}).")
                except requests.exceptions.RequestException as e:
                    print(f"            ❌ Error al crear reserva para {name}: {e}")
                    if e.response:
                        print(f"               Detalle: {e.response.json().get('detail', e.response.text)}")

        except requests.exceptions.RequestException as e:
            print(f"   ❌ Error al crear usuario {name}: {e}")
            if e.response:
                print(f"      Detalle: {e.response.json().get('detail', e.response.text)}")

    print("\n--- Generación de Datos de Prueba Finalizada ---")

if __name__ == "__main__":
    main()
