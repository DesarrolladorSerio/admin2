# Test del Chatbot Público con TinyLlama
$headers = @{
    "Content-Type" = "application/json"
}

$body = @{
    message = "Hola, ¿cómo puedo hacer una reserva de espacios?"
    session_id = $null
} | ConvertTo-Json

Write-Host "Enviando petición al chatbot..." -ForegroundColor Cyan
Write-Host "Body: $body" -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri "http://localhost/api/chatbot/chat/public" -Method POST -Headers $headers -Body $body
    
    Write-Host "`n✅ Respuesta del chatbot:" -ForegroundColor Green
    Write-Host "Session ID: $($response.session_id)" -ForegroundColor Magenta
    Write-Host "Respuesta: $($response.response)" -ForegroundColor White
    
    if ($response.tokens_used) {
        Write-Host "Tokens usados: $($response.tokens_used)" -ForegroundColor Gray
    }
    
    if ($response.response_time_ms) {
        Write-Host "Tiempo de respuesta: $($response.response_time_ms)ms" -ForegroundColor Gray
    }
    
} catch {
    Write-Host "`n❌ Error:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    
    if ($_.ErrorDetails) {
        Write-Host "Detalles: $($_.ErrorDetails.Message)" -ForegroundColor Yellow
    }
}
