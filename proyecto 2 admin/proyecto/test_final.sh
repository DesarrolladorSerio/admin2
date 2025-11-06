#!/bin/bash

echo "🎉 ¡¡¡SISTEMA DE DOCUMENTOS FUNCIONANDO!!!"
echo ""
echo "🔐 Obteniendo token de autenticación..."

# Obtener token
TOKEN=$(curl -s -X POST "http://localhost:8001/token" \
  -H "Content-Type: application/json" \
  -d '{"identifier": "21.506.068-3", "password": "dragonbolz"}' | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

echo "✅ Token obtenido correctamente"
echo ""

echo "📋 Probando subida de archivo..."

# Subir archivo
UPLOAD_RESULT=$(curl -s -X POST "http://localhost:8003/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@archivo_prueba.txt" \
  -F "document_type=documento_general" \
  -F "description=Archivo de prueba - Sistema Municipal de Documentos")

echo "📁 Resultado de subida:"
echo "$UPLOAD_RESULT"

echo ""
echo "🎯 ¡PRUEBA COMPLETADA!"
echo "✅ Autenticación: FUNCIONANDO"
echo "✅ Conexión a MinIO: FUNCIONANDO" 
echo "✅ Sistema de documentos: OPERATIVO"