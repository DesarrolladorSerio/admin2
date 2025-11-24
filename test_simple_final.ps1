$ErrorActionPreference = "Stop"

Write-Host "Probando el chatbot IA..."
Write-Host "Esto puede tomar 2-3 minutos..."

try {
    $body = '{"message": "hola"}'
    
    $response = Invoke-RestMethod -Uri "http://localhost:8081/api/chatbot/chat/public" -Method POST -ContentType "application/json" -Body $body -TimeoutSec 400
    
    Write-Host "El chatbot esta funcionando!"
    Write-Host "Respuesta:"
    Write-Host ($response | ConvertTo-Json -Depth 3)
    Write-Host "Session ID: $($response.session_id)"
    Write-Host "Tokens: $($response.tokens_used)"
    Write-Host "Tiempo: $($response.response_time_ms) ms"
    
} catch {
    Write-Host "Error al probar el chatbot:"
    Write-Host $_.Exception.Message
}