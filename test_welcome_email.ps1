# Test de Notificación de Bienvenida
$body = @{
    user_email    = "brunoganora894@gmail.com"
    user_name     = "Bruno Ganora"
    temp_password = "test123"
} | ConvertTo-Json

Write-Host "Enviando email de bienvenida..." -ForegroundColor Yellow
Write-Host "Body: $body" -ForegroundColor Cyan

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8004/api/notifications/welcome" -Method POST -Body $body -ContentType "application/json"
    Write-Host "Respuesta exitosa:" -ForegroundColor Green
    Write-Host $response.Content -ForegroundColor White
    
    # Extraer el task_id de la respuesta
    $responseObj = $response.Content | ConvertFrom-Json
    $taskId = $responseObj.task_id
    
    Write-Host "Esperando 5 segundos para que se procese el email..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    
    # Consultar el estado de la tarea
    Write-Host "Consultando estado de la tarea: $taskId" -ForegroundColor Yellow
    $statusResponse = Invoke-WebRequest -Uri "http://localhost:8004/api/notifications/task/$taskId" -Method GET
    Write-Host $statusResponse.Content -ForegroundColor White
    
}
catch {
    Write-Host "Error:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}

Write-Host "Por favor revisa tu bandeja de entrada en: brunoganora894@gmail.com" -ForegroundColor Cyan
