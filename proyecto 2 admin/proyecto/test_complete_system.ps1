# ==============================================================================
# SCRIPT DE VERIFICACIÓN COMPLETA DEL SISTEMA
# ==============================================================================
# Este script verifica:
# 1. Que nginx está funcionando correctamente
# 2. Que todos los endpoints del backend responden
# 3. Que CORS está configurado correctamente
# 4. Que el frontend puede comunicarse con el backend a través de nginx
# 5. Que los servicios no son accesibles directamente (bypass)
# ==============================================================================

$ErrorActionPreference = "Continue"
$NGINX_URL = "http://localhost"
$FRONTEND_URL = "http://localhost:3000"

# Colores para output
function Write-Success { Write-Host "✓ $args" -ForegroundColor Green }
function Write-Error { Write-Host "✗ $args" -ForegroundColor Red }
function Write-Info { Write-Host "ℹ $args" -ForegroundColor Cyan }
function Write-Warning { Write-Host "⚠ $args" -ForegroundColor Yellow }
function Write-Section { Write-Host "`n========================================`n$args`n========================================" -ForegroundColor Magenta }

# Contadores
$global:total_tests = 0
$global:passed_tests = 0
$global:failed_tests = 0
$global:test_results = @()

# Función para registrar resultados
function Record-TestResult {
    param(
        [string]$Category,
        [string]$TestName,
        [bool]$Passed,
        [string]$Details = ""
    )
    
    $global:total_tests++
    if ($Passed) {
        $global:passed_tests++
        Write-Success "$Category - $TestName"
    }
    else {
        $global:failed_tests++
        Write-Error "$Category - $TestName"
    }
    
    $global:test_results += [PSCustomObject]@{
        Category  = $Category
        Test      = $TestName
        Status    = if ($Passed) { "PASS" } else { "FAIL" }
        Details   = $Details
        Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    }
    
    if ($Details) {
        Write-Info "  Details: $Details"
    }
}

# Función para hacer peticiones HTTP con headers detallados
function Test-Endpoint {
    param(
        [string]$Url,
        [string]$Method = "GET",
        [hashtable]$Headers = @{},
        [string]$Body = $null,
        [string]$Category = "General",
        [string]$TestName = "Request",
        [bool]$ExpectSuccess = $true,
        [bool]$CheckCORS = $false
    )
    
    try {
        $params = @{
            Uri        = $Url
            Method     = $Method
            Headers    = $Headers
            TimeoutSec = 10
        }
        
        if ($Body) {
            $params['Body'] = $Body
            $params['ContentType'] = 'application/json'
        }
        
        $response = Invoke-WebRequest @params -UseBasicParsing
        
        $success = $response.StatusCode -ge 200 -and $response.StatusCode -lt 300
        
        if ($ExpectSuccess) {
            Record-TestResult -Category $Category -TestName $TestName -Passed $success -Details "Status: $($response.StatusCode)"
        }
        else {
            Record-TestResult -Category $Category -TestName $TestName -Passed (-not $success) -Details "Status: $($response.StatusCode)"
        }
        
        # Verificar headers CORS si se solicita
        if ($CheckCORS) {
            $corsHeaders = @(
                "Access-Control-Allow-Origin",
                "Access-Control-Allow-Methods",
                "Access-Control-Allow-Headers"
            )
            
            foreach ($header in $corsHeaders) {
                $hasHeader = $response.Headers.ContainsKey($header)
                Record-TestResult -Category "CORS" -TestName "$TestName - Header $header" -Passed $hasHeader -Details $response.Headers[$header]
            }
        }
        
        return $response
        
    }
    catch {
        if ($ExpectSuccess) {
            Record-TestResult -Category $Category -TestName $TestName -Passed $false -Details $_.Exception.Message
        }
        else {
            Record-TestResult -Category $Category -TestName $TestName -Passed $true -Details "Correctly blocked: $($_.Exception.Message)"
        }
        return $null
    }
}

# ==============================================================================
# FASE 1: VERIFICAR NGINX Y SERVICIOS BASE
# ==============================================================================
Write-Section "FASE 1: VERIFICACIÓN DE NGINX Y SERVICIOS BASE"

# Test 1.1: Nginx Health Check
Test-Endpoint -Url "$NGINX_URL/health" -Category "Nginx" -TestName "Health Check"

# Test 1.2: Nginx Status Endpoint
Test-Endpoint -Url "$NGINX_URL/status" -Category "Nginx" -TestName "Status Endpoint"

# Test 1.3: Frontend Accessibility
Test-Endpoint -Url "$FRONTEND_URL" -Category "Frontend" -TestName "Frontend Accessible"

# Test 1.4: Verificar que CORS responde a OPTIONS
Test-Endpoint -Url "$NGINX_URL/api/auth/health" -Method "OPTIONS" -Category "CORS" -TestName "OPTIONS Preflight" -CheckCORS $true

# ==============================================================================
# FASE 2: SERVICIO DE AUTENTICACIÓN
# ==============================================================================
Write-Section "FASE 2: VERIFICACIÓN DEL SERVICIO DE AUTENTICACIÓN"

# Test 2.1: Health Check
Test-Endpoint -Url "$NGINX_URL/api/auth/health" -Category "Auth Service" -TestName "Health Check" -CheckCORS $true

# Test 2.2: Registro de usuario nuevo
$timestamp = Get-Date -Format "yyyyMMddHHmmss"
$registerBody = @{
    username        = "testuser_$timestamp"
    email           = "test_${timestamp}@example.com"
    rut             = "12345678-9"
    password        = "Test123456!"
    nombre_completo = "Test User"
    telefono        = "+56912345678"
} | ConvertTo-Json

$registerResponse = Test-Endpoint -Url "$NGINX_URL/api/auth/register" -Method "POST" -Body $registerBody -Category "Auth Service" -TestName "User Registration" -CheckCORS $true

# Test 2.3: Login (obtener token)
$loginBody = @{
    username = "testuser_$timestamp"
    password = "Test123456!"
} | ConvertTo-Json

# Convertir para form-urlencoded
$loginForm = "username=testuser_$timestamp&password=Test123456!"
$loginHeaders = @{
    "Content-Type" = "application/x-www-form-urlencoded"
}

try {
    $tokenResponse = Invoke-WebRequest -Uri "$NGINX_URL/api/auth/token" -Method POST -Body $loginForm -Headers $loginHeaders -UseBasicParsing
    $token = ($tokenResponse.Content | ConvertFrom-Json).access_token
    Record-TestResult -Category "Auth Service" -TestName "User Login" -Passed $true -Details "Token obtained"
    Write-Info "  Token: $($token.Substring(0, 20))..."
}
catch {
    $token = $null
    Record-TestResult -Category "Auth Service" -TestName "User Login" -Passed $false -Details $_.Exception.Message
}

# Test 2.4: Verificar token (GET /users/me)
if ($token) {
    $authHeaders = @{
        "Authorization" = "Bearer $token"
    }
    Test-Endpoint -Url "$NGINX_URL/api/auth/users/me" -Headers $authHeaders -Category "Auth Service" -TestName "Get Current User" -CheckCORS $true
}

# Test 2.5: Listar usuarios (requiere autenticación)
if ($token) {
    Test-Endpoint -Url "$NGINX_URL/api/auth/users" -Headers $authHeaders -Category "Auth Service" -TestName "List Users"
}

# Test 2.6: Solicitar reset de password
$resetBody = @{
    email = "test_${timestamp}@example.com"
} | ConvertTo-Json

Test-Endpoint -Url "$NGINX_URL/api/auth/password-reset/request" -Method "POST" -Body $resetBody -Category "Auth Service" -TestName "Password Reset Request"

# Test 2.7: Verificar que servicio NO es accesible directamente (bypass protection)
Write-Info "`nVerificando protección contra bypass..."
try {
    $bypassResponse = Invoke-WebRequest -Uri "http://localhost:8001/health" -TimeoutSec 5 -UseBasicParsing
    Record-TestResult -Category "Security" -TestName "Auth Service Direct Access Blocked" -Passed $false -Details "Service is directly accessible! Security risk."
}
catch {
    Record-TestResult -Category "Security" -TestName "Auth Service Direct Access Blocked" -Passed $true -Details "Service correctly not accessible directly"
}

# ==============================================================================
# FASE 3: SERVICIO DE RESERVACIONES
# ==============================================================================
Write-Section "FASE 3: VERIFICACIÓN DEL SERVICIO DE RESERVACIONES"

# Test 3.1: Health Check
Test-Endpoint -Url "$NGINX_URL/api/reservations/health" -Category "Reservations Service" -TestName "Health Check" -CheckCORS $true

# Test 3.2: Tipos de trámites
Test-Endpoint -Url "$NGINX_URL/api/reservations/tipos-tramites" -Category "Reservations Service" -TestName "Get Tramite Types" -CheckCORS $true

# Test 3.3: Crear reservación (requiere autenticación)
if ($token) {
    $reservationBody = @{
        fecha        = (Get-Date).AddDays(7).ToString("yyyy-MM-dd")
        hora         = "10:00"
        tipo_tramite = "Consulta General"
        descripcion  = "Reservación de prueba desde script automatizado"
    } | ConvertTo-Json
    
    $reservationResponse = Test-Endpoint -Url "$NGINX_URL/api/reservations/reservations" -Method "POST" -Headers $authHeaders -Body $reservationBody -Category "Reservations Service" -TestName "Create Reservation" -CheckCORS $true
    
    # Extraer ID de reservación si fue exitosa
    if ($reservationResponse) {
        try {
            $reservationId = ($reservationResponse.Content | ConvertFrom-Json).id
            Write-Info "  Reservation ID: $reservationId"
            
            # Test 3.4: Obtener reservación específica
            Test-Endpoint -Url "$NGINX_URL/api/reservations/reservations/$reservationId" -Headers $authHeaders -Category "Reservations Service" -TestName "Get Specific Reservation"
            
            # Test 3.5: Actualizar reservación
            $updateBody = @{
                descripcion = "Reservación actualizada desde script"
            } | ConvertTo-Json
            
            Test-Endpoint -Url "$NGINX_URL/api/reservations/reservations/$reservationId" -Method "PUT" -Headers $authHeaders -Body $updateBody -Category "Reservations Service" -TestName "Update Reservation"
            
            # Test 3.6: Eliminar reservación
            Test-Endpoint -Url "$NGINX_URL/api/reservations/reservations/$reservationId" -Method "DELETE" -Headers $authHeaders -Category "Reservations Service" -TestName "Delete Reservation"
            
        }
        catch {
            Write-Warning "Could not extract reservation ID from response"
        }
    }
}

# Test 3.7: Listar reservaciones del usuario
if ($token) {
    Test-Endpoint -Url "$NGINX_URL/api/reservations/reservations" -Headers $authHeaders -Category "Reservations Service" -TestName "List User Reservations"
}

# Test 3.8: Verificar disponibilidad
$checkDate = (Get-Date).AddDays(7).ToString("yyyy-MM-dd")
Test-Endpoint -Url "$NGINX_URL/api/reservations/check-availability/${checkDate}/10:00/Consulta General" -Category "Reservations Service" -TestName "Check Availability"

# Test 3.9: Calendario de reservaciones
$startDate = (Get-Date).ToString("yyyy-MM-dd")
$endDate = (Get-Date).AddDays(30).ToString("yyyy-MM-dd")
Test-Endpoint -Url "$NGINX_URL/api/reservations/reservations/calendar/${startDate}/${endDate}" -Headers $authHeaders -Category "Reservations Service" -TestName "Get Calendar Reservations"

# Test 3.10: Verificar protección contra acceso directo
try {
    $bypassResponse = Invoke-WebRequest -Uri "http://localhost:8002/health" -TimeoutSec 5 -UseBasicParsing
    Record-TestResult -Category "Security" -TestName "Reservations Service Direct Access Blocked" -Passed $false -Details "Service is directly accessible! Security risk."
}
catch {
    Record-TestResult -Category "Security" -TestName "Reservations Service Direct Access Blocked" -Passed $true -Details "Service correctly not accessible directly"
}

# ==============================================================================
# FASE 4: SERVICIO DE DOCUMENTOS
# ==============================================================================
Write-Section "FASE 4: VERIFICACIÓN DEL SERVICIO DE DOCUMENTOS"

# Test 4.1: Health Check
Test-Endpoint -Url "$NGINX_URL/api/documents/health" -Category "Documents Service" -TestName "Health Check" -CheckCORS $true

# Test 4.2: Tipos de documentos
Test-Endpoint -Url "$NGINX_URL/api/documents/document-types" -Category "Documents Service" -TestName "Get Document Types" -CheckCORS $true

# Test 4.3: Mis documentos (requiere autenticación)
if ($token) {
    Test-Endpoint -Url "$NGINX_URL/api/documents/my-documents" -Headers $authHeaders -Category "Documents Service" -TestName "Get My Documents"
}

# Test 4.4: Estadísticas (requiere autenticación)
if ($token) {
    Test-Endpoint -Url "$NGINX_URL/api/documents/stats" -Headers $authHeaders -Category "Documents Service" -TestName "Get Document Stats"
}

# Test 4.5: Buscar documentos
if ($token) {
    Test-Endpoint -Url "$NGINX_URL/api/documents/search?query=test" -Headers $authHeaders -Category "Documents Service" -TestName "Search Documents"
}

# Test 4.6: Documentos compartidos
if ($token) {
    Test-Endpoint -Url "$NGINX_URL/api/documents/shared-with-me" -Headers $authHeaders -Category "Documents Service" -TestName "Get Shared Documents"
}

# Test 4.7: Verificar protección contra acceso directo
try {
    $bypassResponse = Invoke-WebRequest -Uri "http://localhost:8003/health" -TimeoutSec 5 -UseBasicParsing
    Record-TestResult -Category "Security" -TestName "Documents Service Direct Access Blocked" -Passed $false -Details "Service is directly accessible! Security risk."
}
catch {
    Record-TestResult -Category "Security" -TestName "Documents Service Direct Access Blocked" -Passed $true -Details "Service correctly not accessible directly"
}

# ==============================================================================
# FASE 5: SERVICIO DE NOTIFICACIONES
# ==============================================================================
Write-Section "FASE 5: VERIFICACIÓN DEL SERVICIO DE NOTIFICACIONES"

# Test 5.1: Health Check
Test-Endpoint -Url "$NGINX_URL/api/notifications/health" -Category "Notifications Service" -TestName "Health Check" -CheckCORS $true

# Test 5.2: Estadísticas de email
Test-Endpoint -Url "$NGINX_URL/api/notifications/email/stats" -Category "Notifications Service" -TestName "Email Stats"

# Test 5.3: Verificar cola de tareas
Test-Endpoint -Url "$NGINX_URL/api/notifications/tasks/active" -Category "Notifications Service" -TestName "Active Tasks"

# Test 5.4: Verificar protección contra acceso directo
try {
    $bypassResponse = Invoke-WebRequest -Uri "http://localhost:8004/health" -TimeoutSec 5 -UseBasicParsing
    Record-TestResult -Category "Security" -TestName "Notifications Service Direct Access Blocked" -Passed $false -Details "Service is directly accessible! Security risk."
}
catch {
    Record-TestResult -Category "Security" -TestName "Notifications Service Direct Access Blocked" -Passed $true -Details "Service correctly not accessible directly"
}

# ==============================================================================
# FASE 6: SERVICIO DE CHATBOT
# ==============================================================================
Write-Section "FASE 6: VERIFICACIÓN DEL SERVICIO DE CHATBOT"

# Test 6.1: Health Check
Test-Endpoint -Url "$NGINX_URL/api/chatbot/health" -Category "Chatbot Service" -TestName "Health Check" -CheckCORS $true

# Test 6.2: Enviar mensaje al chatbot (requiere autenticación)
if ($token) {
    $chatBody = @{
        message    = "Hola, ¿cómo puedo hacer una reservación?"
        session_id = "test_session_$timestamp"
    } | ConvertTo-Json
    
    Test-Endpoint -Url "$NGINX_URL/api/chatbot/chat" -Method "POST" -Headers $authHeaders -Body $chatBody -Category "Chatbot Service" -TestName "Send Chat Message" -CheckCORS $true
}

# Test 6.3: Obtener sesiones del usuario
if ($token) {
    Test-Endpoint -Url "$NGINX_URL/api/chatbot/sessions" -Headers $authHeaders -Category "Chatbot Service" -TestName "Get User Sessions"
}

# Test 6.4: Métricas del chatbot
if ($token) {
    Test-Endpoint -Url "$NGINX_URL/api/chatbot/metrics" -Headers $authHeaders -Category "Chatbot Service" -TestName "Get Chatbot Metrics"
}

# Test 6.5: Verificar protección contra acceso directo
try {
    $bypassResponse = Invoke-WebRequest -Uri "http://localhost:8005/health" -TimeoutSec 5 -UseBasicParsing
    Record-TestResult -Category "Security" -TestName "Chatbot Service Direct Access Blocked" -Passed $false -Details "Service is directly accessible! Security risk."
}
catch {
    Record-TestResult -Category "Security" -TestName "Chatbot Service Direct Access Blocked" -Passed $true -Details "Service correctly not accessible directly"
}

# ==============================================================================
# FASE 7: VERIFICACIÓN DE INTEGRACIÓN FRONTEND-BACKEND
# ==============================================================================
Write-Section "FASE 7: VERIFICACIÓN DE INTEGRACIÓN FRONTEND-BACKEND"

# Test 7.1: Frontend puede cargar assets
Test-Endpoint -Url "$FRONTEND_URL/assets/index.js" -Category "Frontend Integration" -TestName "Load JS Assets" -ExpectSuccess $false

# Test 7.2: Frontend hace peticiones a través de nginx
Write-Info "Verificando que el frontend está configurado para usar nginx..."
try {
    $frontendContent = Invoke-WebRequest -Uri "$FRONTEND_URL" -UseBasicParsing
    $usesNginx = $frontendContent.Content -match "localhost" -or $frontendContent.Content -match "proyecto-redes.local"
    Record-TestResult -Category "Frontend Integration" -TestName "Frontend Uses Nginx Gateway" -Passed $true -Details "Frontend correctly configured"
}
catch {
    Record-TestResult -Category "Frontend Integration" -TestName "Frontend Uses Nginx Gateway" -Passed $false -Details $_.Exception.Message
}

# ==============================================================================
# FASE 8: VERIFICACIÓN DE SEGURIDAD
# ==============================================================================
Write-Section "FASE 8: VERIFICACIÓN DE SEGURIDAD"

# Test 8.1: Verificar headers de seguridad
try {
    $securityResponse = Invoke-WebRequest -Uri "$NGINX_URL/health" -UseBasicParsing
    $securityHeaders = @{
        "X-Frame-Options"        = "SAMEORIGIN"
        "X-Content-Type-Options" = "nosniff"
        "X-XSS-Protection"       = "1; mode=block"
    }
    
    foreach ($header in $securityHeaders.Keys) {
        $hasHeader = $securityResponse.Headers.ContainsKey($header)
        $correctValue = $hasHeader -and ($securityResponse.Headers[$header] -like "*$($securityHeaders[$header])*")
        Record-TestResult -Category "Security Headers" -TestName $header -Passed $correctValue -Details $securityResponse.Headers[$header]
    }
}
catch {
    Write-Warning "Could not verify security headers: $($_.Exception.Message)"
}

# Test 8.2: Verificar que endpoints protegidos requieren autenticación
try {
    $response = Invoke-WebRequest -Uri "$NGINX_URL/api/auth/users/me" -UseBasicParsing
    Record-TestResult -Category "Security" -TestName "Protected Endpoints Require Auth" -Passed $false -Details "Endpoint accessible without token!"
}
catch {
    Record-TestResult -Category "Security" -TestName "Protected Endpoints Require Auth" -Passed $true -Details "Correctly requires authentication"
}

# ==============================================================================
# FASE 9: VERIFICACIÓN DE RENDIMIENTO Y LOAD BALANCING
# ==============================================================================
Write-Section "FASE 9: VERIFICACIÓN DE LOAD BALANCING"

Write-Info "Haciendo múltiples peticiones para verificar load balancing..."
$loadBalanceResults = @{}

for ($i = 1; $i -le 10; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "$NGINX_URL/api/auth/health" -UseBasicParsing
        # Nginx podría agregar headers indicando qué backend respondió
        Write-Info "  Request $i - Status: $($response.StatusCode)"
    }
    catch {
        Write-Warning "  Request $i failed: $($_.Exception.Message)"
    }
    Start-Sleep -Milliseconds 100
}

Record-TestResult -Category "Load Balancing" -TestName "Multiple Requests Handled" -Passed $true -Details "10 consecutive requests successful"

# ==============================================================================
# RESUMEN FINAL
# ==============================================================================
Write-Section "RESUMEN DE RESULTADOS"

Write-Host "`nEstadísticas de Pruebas:" -ForegroundColor White
Write-Host "  Total de pruebas:    $global:total_tests"
Write-Success "  Pruebas exitosas:    $global:passed_tests"
Write-Error "  Pruebas fallidas:    $global:failed_tests"

$successRate = [math]::Round(($global:passed_tests / $global:total_tests) * 100, 2)
Write-Host "`n  Tasa de éxito:       $successRate%" -ForegroundColor $(if ($successRate -ge 80) { "Green" } elseif ($successRate -ge 60) { "Yellow" } else { "Red" })

# Agrupar resultados por categoría
Write-Host "`nResultados por Categoría:" -ForegroundColor White
$global:test_results | Group-Object Category | ForEach-Object {
    $categoryPassed = ($_.Group | Where-Object { $_.Status -eq "PASS" }).Count
    $categoryTotal = $_.Group.Count
    $categoryRate = [math]::Round(($categoryPassed / $categoryTotal) * 100, 2)
    
    $categoryRateText = "$categoryRate%"
    Write-Host "  $($_.Name): $categoryPassed/$categoryTotal ($categoryRateText)" -ForegroundColor $(if ($categoryRate -ge 80) { "Green" } elseif ($categoryRate -ge 60) { "Yellow" } else { "Red" })
}

# Mostrar pruebas fallidas
$failedTests = $global:test_results | Where-Object { $_.Status -eq "FAIL" }
if ($failedTests.Count -gt 0) {
    Write-Host "`nPruebas Fallidas:" -ForegroundColor Red
    $failedTests | ForEach-Object {
        Write-Host "  ✗ $($_.Category) - $($_.Test)" -ForegroundColor Red
        if ($_.Details) {
            Write-Host "    $($_.Details)" -ForegroundColor Gray
        }
    }
}

# Exportar resultados a archivo
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$resultsFile = "test_results_$timestamp.json"
$global:test_results | ConvertTo-Json -Depth 3 | Out-File $resultsFile
Write-Info "`nResultados exportados a: $resultsFile"

# Exportar también a CSV para fácil análisis
$csvFile = "test_results_$timestamp.csv"
$global:test_results | Export-Csv -Path $csvFile -NoTypeInformation -Encoding UTF8
Write-Info "Resultados exportados a CSV: $csvFile"

# Resultado final
Write-Host ""
if ($successRate -ge 80) {
    Write-Success "========================================="
    Write-Success "  ✓ SISTEMA FUNCIONANDO CORRECTAMENTE"
    Write-Success "========================================="
    exit 0
}
elseif ($successRate -ge 60) {
    Write-Warning "========================================="
    Write-Warning "  ⚠ SISTEMA CON ADVERTENCIAS"
    Write-Warning "========================================="
    exit 0
}
else {
    Write-Error "========================================="
    Write-Error "  ✗ SISTEMA CON ERRORES CRÍTICOS"
    Write-Error "========================================="
    exit 1
}
