#!/bin/bash

# URL del API Gateway
URL="http://localhost:80"
LOGIN_ENDPOINT="$URL/api/auth/token"

echo "=================================================="
echo " Iniciando Pruebas de Seguridad (WAF & Rate Limit)"
echo "=================================================="

# 1. Prueba de Bloqueo de User-Agent Malicioso
echo ""
echo " [1/3] Probando bloqueo de User-Agent 'sqlmap'..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -A "sqlmap" "$URL/health")

if [ "$HTTP_CODE" -eq 403 ]; then
    echo " ÉXITO: User-Agent malicioso bloqueado (HTTP 403)"
else
    echo " FALLO: User-Agent malicioso NO bloqueado (HTTP $HTTP_CODE)"
fi

# 2. Prueba de Rate Limiting (Global)
echo ""
echo " [2/3] Probando Rate Limit Global (200 peticiones concurrentes)..."
echo "   Enviando ráfaga..."

# Crear archivo temporal para guardar resultados
RESULTS_FILE="results.txt"
rm -f "$RESULTS_FILE"

# Lanzar 200 peticiones en paralelo
for i in {1..200}; do
    curl -s -o /dev/null -w "%{http_code}\n" "$URL/" >> "$RESULTS_FILE" &
done

# Esperar a que terminen
wait

# Contar 429s
count_429=$(grep -c "429" "$RESULTS_FILE")
rm -f "$RESULTS_FILE"

if [ "$count_429" -gt 0 ]; then
    echo " ÉXITO: Se detectaron $count_429 respuestas HTTP 429 (Too Many Requests)"
else
    echo " FALLO: No se activó el Rate Limit (0 respuestas 429)"
fi

# 3. Prueba de Rate Limiting (Login)
echo ""
echo " [3/3] Probando Rate Limit en Login (más estricto)..."
# Login tiene rate=1r/s, burst=5. Enviamos 20 peticiones.
count_429_login=0
for i in {1..20}; do
    CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$LOGIN_ENDPOINT" -d "username=test&password=test")
    if [ "$CODE" -eq 429 ]; then
        count_429_login=$((count_429_login + 1))
    fi
done

if [ "$count_429_login" -gt 0 ]; then
    echo " ÉXITO: Rate Limit de Login activado ($count_429_login bloqueos)"
else
    echo " FALLO: No se activó el Rate Limit en Login"
fi

echo ""
echo "=================================================="
echo " Pruebas finalizadas."
