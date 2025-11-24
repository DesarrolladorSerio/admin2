# ========================================
# SCRIPT DE PRUEBAS AUTOMATIZADAS
# Sistema Municipal de Reservaciones
# ========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  PRUEBAS AUTOMATIZADAS DEL SISTEMA" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$testResults = @()
$testsPassed = 0
$testsFailed = 0

function Test-Service {
    param(
        [string]$Name,
        [string]$Url,
        [string]$ExpectedStatus = "200"
    )
    
    Write-Host "Probando: $Name..." -NoNewline
    
    try {
        $response = Invoke-WebRequest -Uri $Url -Method GET -TimeoutSec 10 -UseBasicParsing
        
        if ($response.StatusCode -eq $ExpectedStatus) {
            Write-Host " ✅ OK" -ForegroundColor Green
            $script:testsPassed++
            return $true
        } else {
            Write-Host " ❌ FAIL (Status: $($response.StatusCode))" -ForegroundColor Red
            $script:testsFailed++
            return $false
        }
    }
    catch {
        Write-Host " ❌ ERROR: $($_.Exception.Message)" -ForegroundColor Red
        $script:testsFailed++
        return $false
    }
}

# ========================================
# 1. PRUEBAS DE SERVICIOS PRINCIPALES
# ========================================
Write-Host "`n1. SERVICIOS PRINCIPALES" -ForegroundColor Yellow
Write-Host "------------------------" -ForegroundColor Yellow

Test-Service -Name "Frontend" -Url "http://localhost:3000"
Test-Service -Name "API Gateway" -Url "http://localhost:80"
Test-Service -Name "Auth Service" -Url "http://localhost:8000/health"
Test-Service -Name "Reservations Service" -Url "http://localhost:8002/health"
Test-Service -Name "Documents Service" -Url "http://localhost:8003/health"
Test-Service -Name "Notifications Service" -Url "http://localhost:8004/health"
Test-Service -Name "ChatBot Service" -Url "http://localhost:8005/health"

# ========================================
# 2. PRUEBAS DE IA Y OLLAMA
# ========================================
Write-Host "`n2. SERVICIOS DE IA (100% GRATUITO)" -ForegroundColor Yellow
Write-Host "-----------------------------------" -ForegroundColor Yellow

Test-Service -Name "Ollama Service" -Url "http://localhost:11434/api/tags"

# Verificar modelo Llama 2
Write-Host "Verificando modelo Llama 2..." -NoNewline
try {
    $ollamaResponse = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -Method GET -UseBasicParsing
    $models = $ollamaResponse.Content | ConvertFrom-Json
    
    if ($models.models.name -contains "llama2:latest") {
        Write-Host " ✅ Modelo Llama 2 instalado" -ForegroundColor Green
        $script:testsPassed++
    } else {
        Write-Host " ❌ Modelo Llama 2 NO encontrado" -ForegroundColor Red
        $script:testsFailed++
    }
}
catch {
    Write-Host " ❌ ERROR verificando modelo" -ForegroundColor Red
    $script:testsFailed++
}

# ========================================
# 3. PRUEBAS DE MONITOREO
# ========================================
Write-Host "`n3. SERVICIOS DE MONITOREO" -ForegroundColor Yellow
Write-Host "--------------------------" -ForegroundColor Yellow

Test-Service -Name "Prometheus" -Url "http://localhost:9090/-/healthy"
Test-Service -Name "Grafana" -Url "http://localhost:3001/api/health"
Test-Service -Name "Alertmanager" -Url "http://localhost:9093/-/healthy"

# ========================================
# 4. PRUEBAS DE EXPORTERS
# ========================================
Write-Host "`n4. EXPORTERS DE MÉTRICAS" -ForegroundColor Yellow
Write-Host "-------------------------" -ForegroundColor Yellow

Test-Service -Name "Node Exporter" -Url "http://localhost:9100/metrics"
Test-Service -Name "Redis Exporter" -Url "http://localhost:9121/metrics"
Test-Service -Name "Postgres Exporter (Auth)" -Url "http://localhost:9187/metrics"
Test-Service -Name "Postgres Exporter (Reservations)" -Url "http://localhost:9188/metrics"
Test-Service -Name "Postgres Exporter (Documents)" -Url "http://localhost:9189/metrics"
Test-Service -Name "Postgres Exporter (ChatBot)" -Url "http://localhost:9190/metrics"

# ========================================
# 5. PRUEBAS DE ALMACENAMIENTO
# ========================================
Write-Host "`n5. SERVICIOS DE ALMACENAMIENTO" -ForegroundColor Yellow
Write-Host "-------------------------------" -ForegroundColor Yellow

# MinIO API
Write-Host "Probando: MinIO API..." -NoNewline
try {
    $response = Invoke-WebRequest -Uri "http://localhost:9000/minio/health/live" -Method GET -UseBasicParsing -TimeoutSec 10
    Write-Host " ✅ OK" -ForegroundColor Green
    $script:testsPassed++
}
catch {
    Write-Host " ❌ FAIL" -ForegroundColor Red
    $script:testsFailed++
}

# MinIO Console (puede dar 302 redirect)
Write-Host "Probando: MinIO Console..." -NoNewline
try {
    $response = Invoke-WebRequest -Uri "http://localhost:9001" -Method GET -UseBasicParsing -TimeoutSec 10 -MaximumRedirection 0 -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200 -or $response.StatusCode -eq 302) {
        Write-Host " ✅ OK" -ForegroundColor Green
        $script:testsPassed++
    } else {
        Write-Host " ❌ FAIL" -ForegroundColor Red
        $script:testsFailed++
    }
}
catch {
    if ($_.Exception.Response.StatusCode -eq 302) {
        Write-Host " ✅ OK (Redirect)" -ForegroundColor Green
        $script:testsPassed++
    } else {
        Write-Host " ❌ FAIL" -ForegroundColor Red
        $script:testsFailed++
    }
}

# Redis
Write-Host "Probando: Redis Cache..." -NoNewline
try {
    $redisTest = docker exec redis_queue redis-cli PING 2>$null
    if ($redisTest -eq "PONG") {
        Write-Host " ✅ OK (PONG)" -ForegroundColor Green
        $script:testsPassed++
    } else {
        Write-Host " ❌ FAIL" -ForegroundColor Red
        $script:testsFailed++
    }
}
catch {
    Write-Host " ❌ ERROR" -ForegroundColor Red
    $script:testsFailed++
}

# ========================================
# 6. PRUEBAS DE BASES DE DATOS
# ========================================
Write-Host "`n6. BASES DE DATOS POSTGRESQL" -ForegroundColor Yellow
Write-Host "-----------------------------" -ForegroundColor Yellow

$databases = @(
    @{Name="Auth DB (Primary)"; Container="auth_db_primary"; DB="auth_db"},
    @{Name="Reservations DB (Primary)"; Container="reservations_db_primary"; DB="reservations_db"},
    @{Name="Documents DB (Primary)"; Container="documents_db_primary"; DB="documents_db"},
    @{Name="ChatBot DB (Primary)"; Container="chatbot_db_primary"; DB="chatbot_db"}
)

foreach ($db in $databases) {
    Write-Host "Probando: $($db.Name)..." -NoNewline
    try {
        $result = docker exec $db.Container psql -U admin -d $db.DB -c "SELECT 1;" 2>$null
        if ($result -match "1 row") {
            Write-Host " ✅ OK" -ForegroundColor Green
            $script:testsPassed++
        } else {
            Write-Host " ❌ FAIL" -ForegroundColor Red
            $script:testsFailed++
        }
    }
    catch {
        Write-Host " ❌ ERROR" -ForegroundColor Red
        $script:testsFailed++
    }
}

# ========================================
# 7. PRUEBA FUNCIONAL: REGISTRO Y LOGIN
# ========================================
Write-Host "`n7. PRUEBA FUNCIONAL: AUTH" -ForegroundColor Yellow
Write-Host "--------------------------" -ForegroundColor Yellow

$timestamp = Get-Date -Format "yyyyMMddHHmmss"
$testUser = "testuser_$timestamp"
$testEmail = "test_$timestamp@example.com"
$testPassword = "Test1234!"

# Registro
Write-Host "Probando: Registro de Usuario..." -NoNewline
try {
    $body = @{
        username = $testUser
        email = $testEmail
        password = $testPassword
        full_name = "Usuario de Prueba"
    } | ConvertTo-Json

    $response = Invoke-WebRequest -Uri "http://localhost:8000/register" -Method POST -Body $body -ContentType "application/json" -UseBasicParsing
    
    if ($response.StatusCode -eq 200 -or $response.StatusCode -eq 201) {
        Write-Host " ✅ OK" -ForegroundColor Green
        $script:testsPassed++
        
        # Login
        Write-Host "Probando: Login de Usuario..." -NoNewline
        Start-Sleep -Seconds 2
        
        $loginBody = @{
            username = $testUser
            password = $testPassword
        } | ConvertTo-Json
        
        $loginResponse = Invoke-WebRequest -Uri "http://localhost:8000/login" -Method POST -Body $loginBody -ContentType "application/json" -UseBasicParsing
        
        if ($loginResponse.StatusCode -eq 200) {
            $loginData = $loginResponse.Content | ConvertFrom-Json
            if ($loginData.access_token) {
                Write-Host " ✅ OK (Token recibido)" -ForegroundColor Green
                $script:testsPassed++
                $global:testToken = $loginData.access_token
            } else {
                Write-Host " ❌ FAIL (No token)" -ForegroundColor Red
                $script:testsFailed++
            }
        } else {
            Write-Host " ❌ FAIL" -ForegroundColor Red
            $script:testsFailed++
        }
    } else {
        Write-Host " ❌ FAIL" -ForegroundColor Red
        $script:testsFailed++
    }
}
catch {
    Write-Host " ❌ ERROR: $($_.Exception.Message)" -ForegroundColor Red
    $script:testsFailed++
}

# ========================================
# 8. VERIFICAR ESTADO DE CONTENEDORES
# ========================================
Write-Host "`n8. ESTADO DE CONTENEDORES" -ForegroundColor Yellow
Write-Host "--------------------------" -ForegroundColor Yellow

Write-Host "Contenedores en ejecución:" -ForegroundColor White
$containers = docker compose ps --format "{{.Name}}" 2>$null
$runningCount = ($containers | Measure-Object).Count
Write-Host "  Total: $runningCount contenedores" -ForegroundColor Cyan

Write-Host "`nContenedores 'Healthy':" -ForegroundColor White
$healthyContainers = docker compose ps --filter "health=healthy" --format "{{.Name}}" 2>$null
$healthyCount = ($healthyContainers | Measure-Object).Count
Write-Host "  Total: $healthyCount contenedores" -ForegroundColor Green

Write-Host "`nContenedores con problemas:" -ForegroundColor White
$problemContainers = docker compose ps --filter "health=unhealthy" --format "{{.Name}}" 2>$null
if ($problemContainers) {
    foreach ($container in $problemContainers) {
        Write-Host "  ⚠️  $container" -ForegroundColor Red
    }
} else {
    Write-Host "  ✅ Ninguno" -ForegroundColor Green
}

# ========================================
# RESUMEN FINAL
# ========================================
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  RESUMEN DE PRUEBAS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$totalTests = $testsPassed + $testsFailed
$successRate = [math]::Round(($testsPassed / $totalTests) * 100, 2)

Write-Host "`nTotal de pruebas: $totalTests" -ForegroundColor White
Write-Host "Exitosas: $testsPassed" -ForegroundColor Green
Write-Host "Fallidas: $testsFailed" -ForegroundColor Red
Write-Host "Tasa de éxito: $successRate%" -ForegroundColor $(if ($successRate -ge 90) { "Green" } elseif ($successRate -ge 70) { "Yellow" } else { "Red" })

Write-Host "`nContenedores Healthy: $healthyCount / $runningCount" -ForegroundColor $(if ($healthyCount -eq $runningCount) { "Green" } else { "Yellow" })

# Guardar resultados en archivo
$reportFile = "test_results_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"
$report = @"
========================================
REPORTE DE PRUEBAS AUTOMATIZADAS
Sistema Municipal de Reservaciones
========================================

Fecha: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')

RESULTADOS:
- Total de pruebas: $totalTests
- Exitosas: $testsPassed
- Fallidas: $testsFailed
- Tasa de éxito: $successRate%

CONTENEDORES:
- Total en ejecución: $runningCount
- Healthy: $healthyCount

========================================
"@

$report | Out-File -FilePath $reportFile -Encoding UTF8

Write-Host "`n📄 Reporte guardado en: $reportFile" -ForegroundColor Cyan

# Evaluación final
Write-Host "`n========================================" -ForegroundColor Cyan
if ($testsFailed -eq 0 -and $healthyCount -eq $runningCount) {
    Write-Host "  ✅ SISTEMA COMPLETAMENTE FUNCIONAL" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    exit 0
} elseif ($successRate -ge 80) {
    Write-Host "  ⚠️  SISTEMA FUNCIONAL CON ADVERTENCIAS" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Cyan
    exit 1
} else {
    Write-Host "  ❌ SISTEMA CON ERRORES CRÍTICOS" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Cyan
    exit 2
}
