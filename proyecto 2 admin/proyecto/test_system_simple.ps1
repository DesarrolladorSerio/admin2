# ==============================================================================
# SCRIPT SIMPLE DE VERIFICACIÓN DEL SISTEMA
# ==============================================================================

$ErrorActionPreference = "Continue"
$NGINX_URL = "http://localhost"

function Write-Success { Write-Host "✓ $args" -ForegroundColor Green }
function Write-Fail { Write-Host "✗ $args" -ForegroundColor Red }
function Write-Info { Write-Host "ℹ $args" -ForegroundColor Cyan }
function Write-Section { Write-Host "`n==================== $args ====================" -ForegroundColor Magenta }

$passed = 0
$failed = 0
$results = @()

function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Url,
        [string]$Method = "GET",
        [hashtable]$Headers = @{},
        [string]$Body = $null
    )
    
    try {
        $params = @{
            Uri             = $Url
            Method          = $Method
            Headers         = $Headers
            TimeoutSec      = 10
            UseBasicParsing = $true
        }
        
        if ($Body) {
            $params['Body'] = $Body
            $params['ContentType'] = 'application/json'
        }
        
        $response = Invoke-WebRequest @params
        
        if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 300) {
            Write-Success "$Name - Status: $($response.StatusCode)"
            $script:passed++
            $script:results += [PSCustomObject]@{ Test = $Name; Status = "PASS"; Details = "Status: $($response.StatusCode)" }
            return $response
        }
        else {
            Write-Fail "$Name - Status: $($response.StatusCode)"
            $script:failed++
            $script:results += [PSCustomObject]@{ Test = $Name; Status = "FAIL"; Details = "Status: $($response.StatusCode)" }
            return $null
        }
    }
    catch {
        Write-Fail "$Name - Error: $($_.Exception.Message)"
        $script:failed++
        $script:results += [PSCustomObject]@{ Test = $Name; Status = "FAIL"; Details = $_.Exception.Message }
        return $null
    }
}

# ==============================================================================
# VERIFICACIÓN DE NGINX
# ==============================================================================
Write-Section "VERIFICACIÓN DE NGINX"

Test-Endpoint -Name "Nginx Health" -Url "$NGINX_URL/health"
Test-Endpoint -Name "Nginx Status" -Url "$NGINX_URL/status"
Test-Endpoint -Name "Frontend" -Url "http://localhost:3000"

# ==============================================================================
# SERVICIO DE AUTENTICACIÓN
# ==============================================================================
Write-Section "SERVICIO DE AUTENTICACIÓN"

Test-Endpoint -Name "Auth Health" -Url "$NGINX_URL/api/auth/health"

# Registro
$timestamp = Get-Date -Format "yyyyMMddHHmmss"
$registerBody = @{
    username        = "testuser_$timestamp"
    email           = "test_${timestamp}@example.com"
    rut             = "12345678-9"
    password        = "Test123456!"
    nombre_completo = "Test User"
    telefono        = "+56912345678"
} | ConvertTo-Json

Write-Info "Registrando usuario de prueba..."
$regResponse = Test-Endpoint -Name "User Registration" -Url "$NGINX_URL/api/auth/register" -Method "POST" -Body $registerBody

# Login
Write-Info "Haciendo login..."
$loginForm = "username=testuser_$timestamp" + [char]38 + "password=Test123456!"
$loginHeaders = @{ "Content-Type" = "application/x-www-form-urlencoded" }

try {
    $tokenResponse = Invoke-WebRequest -Uri "$NGINX_URL/api/auth/token" -Method POST -Body $loginForm -Headers $loginHeaders -UseBasicParsing
    $token = ($tokenResponse.Content | ConvertFrom-Json).access_token
    Write-Success "Login exitoso - Token obtenido"
    $script:passed++
    $script:results += [PSCustomObject]@{ Test = "User Login"; Status = "PASS"; Details = "Token obtained" }
}
catch {
    Write-Fail "Login falló - $($_.Exception.Message)"
    $script:failed++
    $script:results += [PSCustomObject]@{ Test = "User Login"; Status = "FAIL"; Details = $_.Exception.Message }
    $token = $null
}

# Verificar token
if ($token) {
    $authHeaders = @{ "Authorization" = "Bearer $token" }
    Test-Endpoint -Name "Get Current User" -Url "$NGINX_URL/api/auth/users/me" -Headers $authHeaders
    Test-Endpoint -Name "List Users" -Url "$NGINX_URL/api/auth/users" -Headers $authHeaders
}

# ==============================================================================
# SERVICIO DE RESERVACIONES
# ==============================================================================
Write-Section "SERVICIO DE RESERVACIONES"

Test-Endpoint -Name "Reservations Health" -Url "$NGINX_URL/api/reservations/health"
Test-Endpoint -Name "Get Tramite Types" -Url "$NGINX_URL/api/reservations/tipos-tramites"

if ($token) {
    $reservationBody = @{
        fecha        = (Get-Date).AddDays(7).ToString("yyyy-MM-dd")
        hora         = "10:00"
        tipo_tramite = "Consulta General"
        descripcion  = "Reservación de prueba"
    } | ConvertTo-Json
    
    Write-Info "Creando reservación..."
    $resResponse = Test-Endpoint -Name "Create Reservation" -Url "$NGINX_URL/api/reservations/reservations" -Method "POST" -Headers $authHeaders -Body $reservationBody
    
    Test-Endpoint -Name "List User Reservations" -Url "$NGINX_URL/api/reservations/reservations" -Headers $authHeaders
}

# ==============================================================================
# SERVICIO DE DOCUMENTOS
# ==============================================================================
Write-Section "SERVICIO DE DOCUMENTOS"

Test-Endpoint -Name "Documents Health" -Url "$NGINX_URL/api/documents/health"
Test-Endpoint -Name "Get Document Types" -Url "$NGINX_URL/api/documents/document-types"

if ($token) {
    Test-Endpoint -Name "Get My Documents" -Url "$NGINX_URL/api/documents/my-documents" -Headers $authHeaders
}

# ==============================================================================
# SERVICIO DE NOTIFICACIONES
# ==============================================================================
Write-Section "SERVICIO DE NOTIFICACIONES"

Test-Endpoint -Name "Notifications Health" -Url "$NGINX_URL/api/notifications/health"
Test-Endpoint -Name "Email Stats" -Url "$NGINX_URL/api/notifications/email/stats"

# ==============================================================================
# SERVICIO DE CHATBOT
# ==============================================================================
Write-Section "SERVICIO DE CHATBOT"

Test-Endpoint -Name "Chatbot Health" -Url "$NGINX_URL/api/chatbot/health"

if ($token) {
    $chatBody = @{
        message    = "Hola, necesito información"
        session_id = "test_session_$timestamp"
    } | ConvertTo-Json
    
    Test-Endpoint -Name "Send Chat Message" -Url "$NGINX_URL/api/chatbot/chat" -Method "POST" -Headers $authHeaders -Body $chatBody
}

# ==============================================================================
# VERIFICACIÓN DE SEGURIDAD
# ==============================================================================
Write-Section "VERIFICACIÓN DE SEGURIDAD"

# Verificar que servicios NO son accesibles directamente
$ports = @(
    @{ Name = "Auth Service"; Port = 8001 },
    @{ Name = "Reservations Service"; Port = 8002 },
    @{ Name = "Documents Service"; Port = 8003 },
    @{ Name = "Notifications Service"; Port = 8004 },
    @{ Name = "Chatbot Service"; Port = 8005 }
)

foreach ($service in $ports) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$($service.Port)/health" -TimeoutSec 5 -UseBasicParsing
        Write-Fail "$($service.Name) - Accesible directamente (RIESGO DE SEGURIDAD)"
        $script:failed++
        $script:results += [PSCustomObject]@{ Test = "$($service.Name) Direct Access Blocked"; Status = "FAIL"; Details = "Service is directly accessible" }
    }
    catch {
        Write-Success "$($service.Name) - Correctamente bloqueado"
        $script:passed++
        $script:results += [PSCustomObject]@{ Test = "$($service.Name) Direct Access Blocked"; Status = "PASS"; Details = "Service not directly accessible" }
    }
}

# Verificar CORS headers
Write-Info "Verificando headers CORS..."
try {
    $corsResponse = Invoke-WebRequest -Uri "$NGINX_URL/api/auth/health" -Method OPTIONS -UseBasicParsing
    $hasCors = $corsResponse.Headers.ContainsKey("Access-Control-Allow-Origin")
    
    if ($hasCors) {
        Write-Success "CORS Headers - Presentes"
        $script:passed++
        $script:results += [PSCustomObject]@{ Test = "CORS Headers Present"; Status = "PASS"; Details = "CORS configured" }
    }
    else {
        Write-Fail "CORS Headers - Ausentes"
        $script:failed++
        $script:results += [PSCustomObject]@{ Test = "CORS Headers Present"; Status = "FAIL"; Details = "CORS not configured" }
    }
}
catch {
    Write-Fail "CORS Check - Error: $($_.Exception.Message)"
    $script:failed++
    $script:results += [PSCustomObject]@{ Test = "CORS Headers Present"; Status = "FAIL"; Details = $_.Exception.Message }
}

# ==============================================================================
# RESUMEN FINAL
# ==============================================================================
Write-Section "RESUMEN"

$total = $passed + $failed
$successRate = if ($total -gt 0) { [math]::Round(($passed / $total) * 100, 2) } else { 0 }

Write-Host "`nEstadísticas:" -ForegroundColor White
Write-Host "  Total de pruebas:    $total"
Write-Success "  Pruebas exitosas:    $passed"
Write-Fail "  Pruebas fallidas:    $failed"
Write-Host "  Tasa de éxito:       $successRate%" -ForegroundColor $(if ($successRate -ge 80) { "Green" } elseif ($successRate -ge 60) { "Yellow" } else { "Red" })

# Exportar resultados
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$resultsFile = "test_results_$timestamp.json"
$results | ConvertTo-Json | Out-File $resultsFile
Write-Info "`nResultados exportados a: $resultsFile"

$csvFile = "test_results_$timestamp.csv"
$results | Export-Csv -Path $csvFile -NoTypeInformation
Write-Info "Resultados exportados a: $csvFile"

# Mostrar pruebas fallidas
$failedTests = $results | Where-Object { $_.Status -eq "FAIL" }
if ($failedTests.Count -gt 0) {
    Write-Host "`nPruebas Fallidas:" -ForegroundColor Red
    $failedTests | ForEach-Object {
        Write-Host "  ✗ $($_.Test) - $($_.Details)" -ForegroundColor Red
    }
}

# Resultado final
Write-Host ""
if ($successRate -ge 80) {
    Write-Success "========================================="
    Write-Success "  SISTEMA FUNCIONANDO CORRECTAMENTE"
    Write-Success "========================================="
    exit 0
}
elseif ($successRate -ge 60) {
    Write-Host "=========================================" -ForegroundColor Yellow
    Write-Host "  SISTEMA CON ADVERTENCIAS" -ForegroundColor Yellow
    Write-Host "=========================================" -ForegroundColor Yellow
    exit 0
}
else {
    Write-Fail "========================================="
    Write-Fail "  SISTEMA CON ERRORES CRÍTICOS"
    Write-Fail "========================================="
    exit 1
}
