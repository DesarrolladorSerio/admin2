#!/bin/bash

# Smoke Test Script v5 (corrigiendo -w de curl)

echo "--- Iniciando Smoke Test de Endpoints (v5) ---"

# URL del gateway
BASE_URL="http://localhost"

# Credenciales
ADMIN_USER="admin@municipalidad.cl"
ADMIN_PASS="admin123"

# --- Autenticación ---
echo "Obteniendo token de administrador..."
LOGIN_PAYLOAD="{\"identifier\":\"$ADMIN_USER\",\"password\":\"$ADMIN_PASS\"}"
LOGIN_RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" -d "$LOGIN_PAYLOAD" "$BASE_URL/api/auth/token")

# Extraer token con sed
TOKEN=$(echo "$LOGIN_RESPONSE" | sed -n 's/.*"access_token":"\([^"]*\)".*/\1/p')

if [ -z "$TOKEN" ]; then
    echo "FALLO: No se pudo obtener el token de autenticación."
    echo "Respuesta recibida: $LOGIN_RESPONSE"
    exit 1
fi
echo "Token obtenido."
echo ""

# --- Pruebas ---
AUTH_HEADER="Authorization: Bearer $TOKEN"
CONTENT_HEADER="Content-Type: application/json"

echo "--- Servicio de Autenticación ---"
http_code=$(curl -s -o /dev/null -w "%{http_code}" -H "$AUTH_HEADER" "$BASE_URL/api/auth/users/me")
echo "GET /api/auth/users/me: $http_code"
http_code=$(curl -s -o /dev/null -w "%{http_code}" -H "$AUTH_HEADER" "$BASE_URL/api/auth/users")
echo "GET /api/auth/users: $http_code"
http_code=$(curl -s -o /dev/null -w "%{http_code}" -H "$AUTH_HEADER" "$BASE_URL/api/auth/admin/licencias-por-vencer")
echo "GET /api/auth/admin/licencias-por-vencer: $http_code"

echo ""
echo "--- Servicio de Reservas ---"
http_code=$(curl -s -o /dev/null -w "%{http_code}" -H "$AUTH_HEADER" "$BASE_URL/api/reservations/reservations")
echo "GET /api/reservations/reservations: $http_code"
http_code=$(curl -s -o /dev/null -w "%{http_code}" -H "$AUTH_HEADER" "$BASE_URL/api/reservations/reservations/my")
echo "GET /api/reservations/reservations/my: $http_code"
http_code=$(curl -s -o /dev/null -w "%{http_code}" -H "$AUTH_HEADER" "$BASE_URL/api/reservations/tipos-tramites")
echo "GET /api/reservations/tipos-tramites: $http_code"
http_code=$(curl -s -o /dev/null -w "%{http_code}" -H "$AUTH_HEADER" "$BASE_URL/api/reservations/admin/dashboard")
echo "GET /api/reservations/admin/dashboard: $http_code"
http_code=$(curl -s -o /dev/null -w "%{http_code}" -H "$AUTH_HEADER" "$BASE_URL/api/reservations/admin/estadisticas-tramites")
echo "GET /api/reservations/admin/estadisticas-tramites: $http_code"
http_code=$(curl -s -o /dev/null -w "%{http_code}" -H "$AUTH_HEADER" "$BASE_URL/api/reservations/admin/reservations")
echo "GET /api/reservations/admin/reservations: $http_code"
http_code=$(curl -s -o /dev/null -w "%{http_code}" -X POST -H "$AUTH_HEADER" -H "$CONTENT_HEADER" -d '{}' "$BASE_URL/api/reservations/admin/buscar-reservas")
echo "POST /api/reservations/admin/buscar-reservas: $http_code"

echo ""
echo "--- Servicio de Documentos ---"
http_code=$(curl -s -o /dev/null -w "%{http_code}" -H "$AUTH_HEADER" "$BASE_URL/api/documents/documentos/usuario/1")
echo "GET /api/documents/documentos/usuario/1: $http_code"
http_code=$(curl -s -o /dev/null -w "%{http_code}" -H "$AUTH_HEADER" "$BASE_URL/api/documents/documentos/reserva/1")
echo "GET /api/documents/documentos/reserva/1: $http_code"
http_code=$(curl -s -o /dev/null -w "%{http_code}" -H "$AUTH_HEADER" "$BASE_URL/api/documents/documentos-antiguos/pendientes")
echo "GET /api/documents/documentos-antiguos/pendientes: $http_code"
http_code=$(curl -s -o /dev/null -w "%{http_code}" -H "$AUTH_HEADER" "$BASE_URL/api/documents/reportes/avance-antiguos")
echo "GET /api/documents/reportes/avance-antiguos: $http_code"
http_code=$(curl -s -o /dev/null -w "%{http_code}" -X POST -H "$AUTH_HEADER" -H "$CONTENT_HEADER" -d '{}' "$BASE_URL/api/documents/documentos-antiguos/buscar")
echo "POST /api/documents/documentos-antiguos/buscar: $http_code"

echo ""
echo "--- Fin del Smoke Test ---"