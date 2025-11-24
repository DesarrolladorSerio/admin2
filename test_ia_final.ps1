Write-Host "🤖 Probando el chatbot IA..." -ForegroundColor Cyan
Write-Host "⏱️ Esto puede tomar 2-3 minutos debido al procesamiento del modelo..." -ForegroundColor Yellow

try {
    $body = '{"message": "hola"}'
    
    Write-Host "📤 Enviando solicitud..." -ForegroundColor Yellow
    $response = Invoke-RestMethod -Uri "http://localhost:8081/api/chatbot/chat/public" -Method POST -ContentType "application/json" -Body $body -TimeoutSec 400
    
    Write-Host "✅ ¡El chatbot está funcionando perfectamente!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Respuesta completa:" -ForegroundColor Cyan
    Write-Host ($response | ConvertTo-Json -Depth 3)
    Write-Host ""
    Write-Host "📊 Estadísticas:" -ForegroundColor Yellow
    Write-Host "   - Session ID: $($response.session_id)"
    Write-Host "   - Tokens utilizados: $($response.tokens_used)"
    Write-Host "   - Tiempo de respuesta: $([math]::Round($response.response_time_ms / 1000, 1)) segundos"
    
} catch {
    Write-Host "❌ Error al probar el chatbot:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}