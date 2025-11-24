$ErrorActionPreference = "Stop"

Write-Host "🤖 Probando el chatbot IA..."
Write-Host "⏱️  Esto puede tomar 2-3 minutos debido al procesamiento del modelo IA"

try {
    $body = '{"message": "hola"}'
    
    $response = Invoke-RestMethod `
        -Uri "http://localhost:8081/api/chatbot/chat/public" `
        -Method POST `
        -ContentType "application/json" `
        -Body $body `
        -TimeoutSec 300
    
    Write-Host "✅ ¡Chatbot funcionando!" -ForegroundColor Green
    Write-Host "📝 Respuesta:" -ForegroundColor Cyan
    Write-Host ($response | ConvertTo-Json -Depth 3)
    
    Write-Host "`n🔍 Información de la respuesta:" -ForegroundColor Yellow
    Write-Host "   - Session ID: $($response.session_id)"
    Write-Host "   - Tokens utilizados: $($response.tokens_used)"
    Write-Host "   - Tiempo de respuesta: $($response.response_time_ms)ms"
    
} catch {
    Write-Host "❌ Error al probar el chatbot:" -ForegroundColor Red
    Write-Host $_.Exception.Message
    exit 1
}