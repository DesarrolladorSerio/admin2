# Script de Verificacion del Sistema
# Verifica que todos los endpoints funcionan correctamente a traves de nginx

$ErrorActionPreference = "Continue"
$NGINX_URL = "http://localhost"

$passed = 0
$failed = 0

function Test-Endpoint {
    param([string]$Name, [string]$Url)
    
    try {
        $response = Invoke-WebRequest -Uri $Url -TimeoutSec 10 -UseBasicParsing
        Write-Host "[PASS] $Name - Status: $($response.StatusCode)" -ForegroundColor Green
        $script:passed++
        return $response
    }
    catch {
        Write-Host "[FAIL] $Name - Error: $($_.Exception.Message)" -ForegroundColor Red
        $script:failed++
        return $null
    }
}

Write-Host "`n========== VERIFICACION DE NGINX ==========" -ForegroundColor Cyan
Test-Endpoint -Name "Nginx Health" -Url "$NGINX_URL/health"
Test-Endpoint -Name "Nginx Status" -Url "$NGINX_URL/status"
Test-Endpoint -Name "Frontend" -Url "http://localhost:3000"

Write-Host "`n========== SERVICIO DE AUTENTICACION ==========" -ForegroundColor Cyan
Test-Endpoint -Name "Auth Health" -Url "$NGINX_URL/api/auth/health"

Write-Host "`n========== SERVICIO DE RESERVACIONES ==========" -ForegroundColor Cyan
Test-Endpoint -Name "Reservations Health" -Url "$NGINX_URL/api/reservations/health"
Test-Endpoint -Name "Tramite Types" -Url "$NGINX_URL/api/reservations/tipos-tramites"

Write-Host "`n========== SERVICIO DE DOCUMENTOS ==========" -ForegroundColor Cyan
Test-Endpoint -Name "Documents Health" -Url "$NGINX_URL/api/documents/health"
Test-Endpoint -Name "Document Types" -Url "$NGINX_URL/api/documents/document-types"

Write-Host "`n========== SERVICIO DE NOTIFICACIONES ==========" -ForegroundColor Cyan
Test-Endpoint -Name "Notifications Health" -Url "$NGINX_URL/api/notifications/health"
Test-Endpoint -Name "Notifications Stats" -Url "$NGINX_URL/api/notifications/stats"

Write-Host "`n========== SERVICIO DE CHATBOT ==========" -ForegroundColor Cyan
Test-Endpoint -Name "Chatbot Health" -Url "$NGINX_URL/api/chatbot/health"

Write-Host "`n========== VERIFICACION DE SEGURIDAD ==========" -ForegroundColor Cyan
Write-Host "Verificando que los servicios NO son accesibles directamente..." -ForegroundColor Yellow

$ports = @(8001, 8002, 8003, 8004, 8005)
foreach ($port in $ports) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$port/health" -TimeoutSec 5 -UseBasicParsing
        Write-Host "[FAIL] Puerto $port - Accesible directamente (RIESGO)" -ForegroundColor Red
        $script:failed++
    }
    catch {
        Write-Host "[PASS] Puerto $port - Correctamente bloqueado" -ForegroundColor Green
        $script:passed++
    }
}

Write-Host "`n========== RESUMEN ==========" -ForegroundColor Magenta
$total = $passed + $failed
$successRate = if ($total -gt 0) { [math]::Round(($passed / $total) * 100, 2) } else { 0 }

Write-Host "Total de pruebas:    $total"
Write-Host "Pruebas exitosas:    $passed" -ForegroundColor Green
Write-Host "Pruebas fallidas:    $failed" -ForegroundColor Red
Write-Host "Tasa de exito:       $successRate%" -ForegroundColor $(if ($successRate -ge 80) { "Green" } else { "Yellow" })

# Guardar resultados
$timestamp = Get-Date -Format "yyyyMMddHHmmss"
$resultsFile = "test_results_$timestamp.txt"
@"
RESULTADOS DE PRUEBAS DEL SISTEMA
Timestamp: $timestamp
Total: $total
Exitosas: $passed
Fallidas: $failed
Tasa de exito: $successRate%
"@ | Out-File $resultsFile

Write-Host "`nResultados guardados en: $resultsFile" -ForegroundColor Cyan

if ($successRate -ge 80) {
    Write-Host "`n[ SISTEMA FUNCIONANDO CORRECTAMENTE ]" -ForegroundColor Green
    exit 0
}
else {
    Write-Host "`n[ SISTEMA CON ERRORES ]" -ForegroundColor Red
    exit 1
}
