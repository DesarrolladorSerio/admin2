#!/bin/bash

echo "🔐 Haciendo login..."
RESPONSE=$(curl -s -X POST "http://localhost:8001/token" \
  -H "Content-Type: application/json" \
  -d '{"identifier": "21.506.068-3", "password": "dragonbolz"}')

echo "Respuesta de login: $RESPONSE"

# Extraer token
TOKEN=$(echo $RESPONSE | jq -r '.access_token')

if [ "$TOKEN" = "null" ]; then
    echo "❌ Error obteniendo token"
    exit 1
fi

echo "✅ Token obtenido: ${TOKEN:0:50}..."

echo ""
echo "🧪 Probando autenticación..."
USER_INFO=$(curl -s -X GET "http://localhost:8001/users/me" \
  -H "Authorization: Bearer $TOKEN")

echo "Info del usuario: $USER_INFO"

echo ""
echo "📁 Probando subida de archivo..."
UPLOAD_RESPONSE=$(curl -s -X POST "http://localhost:8003/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@archivo_prueba.txt" \
  -F "document_type=documento_general" \
  -F "description=Archivo de prueba del sistema municipal")

echo "Respuesta de subida: $UPLOAD_RESPONSE"

echo ""
echo "📋 Obteniendo mis documentos..."
DOCS_RESPONSE=$(curl -s -X GET "http://localhost:8003/my-documents" \
  -H "Authorization: Bearer $TOKEN")

echo "Mis documentos: $DOCS_RESPONSE"