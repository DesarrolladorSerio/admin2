# ===================================================
# 🧪 TEST CORS - Verificación de API Gateway
# ===================================================
# Este script verifica que Nginx maneja CORS correctamente
# para todos los servicios FastAPI
# ===================================================

# ===================================================
# 🧪 TEST CORS - Verificación de API Gateway
# ===================================================

Write-Host "`n🧪 TESTING CORS CONFIGURATION - API Gateway" -ForegroundColor Cyan
Write-Host ("=" * 60) -ForegroundColor Cyan

$gateway_url = "http://localhost"
$test_origin = "http://localhost:3000"

# ===================================================
# Test 1: Preflight Request (OPTIONS)
# ===================================================
Write-Host "`n📋 Test 1: Preflight Request (OPTIONS)" -ForegroundColor Yellow
Write-Host ("-" * 60)

$endpoints = @(
    "/api/auth/users/me",
    "/api/reservations",
    "/api/documents/upload",
    "/api/notifications/send",
    "/api/chatbot/chat"
)

foreach ($endpoint in $endpoints) {
    Write-Host "`n🔹 Testing: $endpoint" -ForegroundColor Green
    
    try {
        $response = Invoke-WebRequest -Uri "$gateway_url$endpoint" -Method OPTIONS -Headers @{
            "Origin"                         = $test_origin
            "Access-Control-Request-Method"  = "POST"
            "Access-Control-Request-Headers" = "Authorization, Content-Type"
        } -SkipHttpErrorCheck -TimeoutSec 5
        
        $statusColor = if ($response.StatusCode -eq 204) { "Green" } else { "Red" }
        Write-Host "   Status: $($response.StatusCode)" -ForegroundColor $statusColor
        
        # Check CORS headers
        if ($response.Headers["Access-Control-Allow-Origin"]) {
            Write-Host "   ✅ Access-Control-Allow-Origin: $($response.Headers['Access-Control-Allow-Origin'])" -ForegroundColor Green
        }
        else {
            Write-Host "   ❌ Access-Control-Allow-Origin: NOT FOUND" -ForegroundColor Red
        }
        
        if ($response.Headers["Access-Control-Allow-Methods"]) {
            Write-Host "   ✅ Access-Control-Allow-Methods: $($response.Headers['Access-Control-Allow-Methods'])" -ForegroundColor Green
        }
        else {
            Write-Host "   ❌ Access-Control-Allow-Methods: NOT FOUND" -ForegroundColor Red
        }
        
    }
    catch {
        Write-Host "   ❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# ===================================================
# Test 2: GET Request with CORS headers
# ===================================================
Write-Host "`n`n📋 Test 2: GET Request with CORS headers" -ForegroundColor Yellow
Write-Host ("-" * 60)

$get_endpoints = @("/status", "/health")

foreach ($endpoint in $get_endpoints) {
    Write-Host "`n🔹 Testing: $endpoint" -ForegroundColor Green
    
    try {
        $response = Invoke-WebRequest -Uri "$gateway_url$endpoint" -Method GET -Headers @{
            "Origin" = $test_origin
        } -SkipHttpErrorCheck -TimeoutSec 5
        
        $statusColor = if ($response.StatusCode -eq 200) { "Green" } else { "Red" }
        Write-Host "   Status: $($response.StatusCode)" -ForegroundColor $statusColor
        
        if ($response.Headers["Access-Control-Allow-Origin"]) {
            Write-Host "   ✅ Access-Control-Allow-Origin: $($response.Headers['Access-Control-Allow-Origin'])" -ForegroundColor Green
        }
        else {
            Write-Host "   ❌ Access-Control-Allow-Origin: NOT FOUND" -ForegroundColor Red
        }
        
        if ($response.Content) {
            Write-Host "   📄 Response: $($response.Content)" -ForegroundColor Cyan
        }
        
    }
    catch {
        Write-Host "   ❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# ===================================================
# Test 3: Security Headers
# ===================================================
Write-Host "`n`n📋 Test 3: Security Headers" -ForegroundColor Yellow
Write-Host ("-" * 60)

try {
    $response = Invoke-WebRequest -Uri "$gateway_url/status" -Method GET -SkipHttpErrorCheck -TimeoutSec 5
    
    Write-Host "`n🔐 Security Headers Check:" -ForegroundColor Green
    
    if ($response.Headers["X-Frame-Options"]) {
        Write-Host "   ✅ X-Frame-Options: $($response.Headers['X-Frame-Options'])" -ForegroundColor Green
    }
    else {
        Write-Host "   ⚠️  X-Frame-Options: NOT FOUND" -ForegroundColor Yellow
    }
    
    if ($response.Headers["X-Content-Type-Options"]) {
        Write-Host "   ✅ X-Content-Type-Options: $($response.Headers['X-Content-Type-Options'])" -ForegroundColor Green
    }
    else {
        Write-Host "   ⚠️  X-Content-Type-Options: NOT FOUND" -ForegroundColor Yellow
    }
    
}
catch {
    Write-Host "   ❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}

# ===================================================
# Summary
# ===================================================
Write-Host "`n`n" -NoNewline
Write-Host ("=" * 60) -ForegroundColor Cyan
Write-Host "✅ CORS TEST COMPLETED" -ForegroundColor Green
Write-Host ("=" * 60) -ForegroundColor Cyan

Write-Host "`n📝 Notes:" -ForegroundColor Yellow
Write-Host "   - All CORS headers should be present in responses" -ForegroundColor White
Write-Host "   - OPTIONS requests should return 204 No Content" -ForegroundColor White
Write-Host "   - Security headers should be applied to all endpoints" -ForegroundColor White

Write-Host "`n"

Write-Host "=" * 60 -ForegroundColor Cyan

$gateway_url = "http://localhost"
$test_origin = "http://localhost:3000"

# ===================================================
# Test 1: Preflight Request (OPTIONS)
# ===================================================
Write-Host "`n📋 Test 1: Preflight Request (OPTIONS)" -ForegroundColor Yellow
Write-Host "-" * 60

$endpoints = @(
    "/api/auth/users/me",
    "/api/reservations",
    "/api/documents/upload",
    "/api/notifications/send",
    "/api/chatbot/chat"
)

foreach ($endpoint in $endpoints) {
    Write-Host "`n🔹 Testing: $endpoint" -ForegroundColor Green
    
    try {
        $response = Invoke-WebRequest -Uri "$gateway_url$endpoint" `
            -Method OPTIONS `
            -Headers @{
            "Origin"                         = $test_origin
            "Access-Control-Request-Method"  = "POST"
            "Access-Control-Request-Headers" = "Authorization, Content-Type"
        } `
            -SkipHttpErrorCheck `
            -TimeoutSec 5
        
        Write-Host "   Status: $($response.StatusCode)" -ForegroundColor $(if ($response.StatusCode -eq 204) { "Green" } else { "Red" })
        
        # Check CORS headers
        $cors_headers = @{
            "Access-Control-Allow-Origin"  = $response.Headers["Access-Control-Allow-Origin"]
            "Access-Control-Allow-Methods" = $response.Headers["Access-Control-Allow-Methods"]
            "Access-Control-Allow-Headers" = $response.Headers["Access-Control-Allow-Headers"]
            "Access-Control-Max-Age"       = $response.Headers["Access-Control-Max-Age"]
        }
        
        foreach ($header in $cors_headers.GetEnumerator()) {
            if ($header.Value) {
                Write-Host "   ✅ $($header.Key): $($header.Value)" -ForegroundColor Green
            }
            else {
                Write-Host "   ❌ $($header.Key): NOT FOUND" -ForegroundColor Red
            }
        }
        
    }
    catch {
        Write-Host "   ❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# ===================================================
# Test 2: GET Request with CORS headers
# ===================================================
Write-Host "`n`n📋 Test 2: GET Request with CORS headers" -ForegroundColor Yellow
Write-Host "-" * 60

$get_endpoints = @(
    "/status",
    "/health"
)

foreach ($endpoint in $get_endpoints) {
    Write-Host "`n🔹 Testing: $endpoint" -ForegroundColor Green
    
    try {
        $response = Invoke-WebRequest -Uri "$gateway_url$endpoint" `
            -Method GET `
            -Headers @{
            "Origin" = $test_origin
        } `
            -SkipHttpErrorCheck `
            -TimeoutSec 5
        
        Write-Host "   Status: $($response.StatusCode)" -ForegroundColor $(if ($response.StatusCode -eq 200) { "Green" } else { "Red" })
        
        # Check CORS headers
        if ($response.Headers["Access-Control-Allow-Origin"]) {
            Write-Host "   ✅ Access-Control-Allow-Origin: $($response.Headers['Access-Control-Allow-Origin'])" -ForegroundColor Green
        }
        else {
            Write-Host "   ❌ Access-Control-Allow-Origin: NOT FOUND" -ForegroundColor Red
        }
        
        if ($response.Headers["Access-Control-Allow-Credentials"]) {
            Write-Host "   ✅ Access-Control-Allow-Credentials: $($response.Headers['Access-Control-Allow-Credentials'])" -ForegroundColor Green
        }
        else {
            Write-Host "   ⚠️  Access-Control-Allow-Credentials: NOT FOUND" -ForegroundColor Yellow
        }
        
        # Show response body for status/health endpoints
        if ($response.Content) {
            Write-Host "   📄 Response: $($response.Content)" -ForegroundColor Cyan
        }
        
    }
    catch {
        Write-Host "   ❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# ===================================================
# Test 3: Security Headers
# ===================================================
Write-Host "`n`n📋 Test 3: Security Headers" -ForegroundColor Yellow
Write-Host "-" * 60

try {
    $response = Invoke-WebRequest -Uri "$gateway_url/status" `
        -Method GET `
        -SkipHttpErrorCheck `
        -TimeoutSec 5
    
    $security_headers = @{
        "X-Frame-Options"         = $response.Headers["X-Frame-Options"]
        "X-Content-Type-Options"  = $response.Headers["X-Content-Type-Options"]
        "X-XSS-Protection"        = $response.Headers["X-XSS-Protection"]
        "Content-Security-Policy" = $response.Headers["Content-Security-Policy"]
    }
    
    Write-Host "`n🔐 Security Headers Check:" -ForegroundColor Green
    foreach ($header in $security_headers.GetEnumerator()) {
        if ($header.Value) {
            Write-Host "   ✅ $($header.Key): $($header.Value)" -ForegroundColor Green
        }
        else {
            Write-Host "   ⚠️  $($header.Key): NOT FOUND" -ForegroundColor Yellow
        }
    }
    
}
catch {
    Write-Host "   ❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}

# ===================================================
# Test 4: Upstream Services Status
# ===================================================
Write-Host "`n`n📋 Test 4: Upstream Services Status" -ForegroundColor Yellow
Write-Host "-" * 60

$services = @{
    "Auth Service 1"         = "http://localhost:8000"
    "Auth Service 2"         = "http://localhost:8001"
    "Reservations Service 1" = "http://localhost:8002"
    "Reservations Service 2" = "http://localhost:8003"
    "Documents Service"      = "http://localhost:8004"
    "Notifications Service"  = "http://localhost:8005"
    "Chatbot Service 1"      = "http://localhost:8006"
    "Chatbot Service 2"      = "http://localhost:8007"
}

Write-Host "`n🔍 Checking backend services..." -ForegroundColor Cyan

foreach ($service in $services.GetEnumerator()) {
    try {
        # Try to hit /docs endpoint (FastAPI default)
        $response = Invoke-WebRequest -Uri "$($service.Value)/docs" `
            -Method GET `
            -SkipHttpErrorCheck `
            -TimeoutSec 3
        
        if ($response.StatusCode -eq 200) {
            Write-Host "   ✅ $($service.Key): Running (Status $($response.StatusCode))" -ForegroundColor Green
        }
        else {
            Write-Host "   ⚠️  $($service.Key): Returned $($response.StatusCode)" -ForegroundColor Yellow
        }
        
    }
    catch {
        Write-Host "   ❌ $($service.Key): Not reachable" -ForegroundColor Red
    }
}

# ===================================================
# Summary
# ===================================================
Write-Host "`n`n" + "=" * 60 -ForegroundColor Cyan
Write-Host "✅ CORS TEST COMPLETED" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Cyan

Write-Host "`n📝 Notes:" -ForegroundColor Yellow
Write-Host "   - All CORS headers should be present in responses" -ForegroundColor White
Write-Host "   - OPTIONS requests should return 204 No Content" -ForegroundColor White
Write-Host "   - Security headers should be applied to all endpoints" -ForegroundColor White
Write-Host "   - Backend services should NOT have CORS middleware" -ForegroundColor White

Write-Host "`n🔧 If tests fail:" -ForegroundColor Yellow
Write-Host "   1. Check nginx.conf configuration" -ForegroundColor White
Write-Host "   2. Restart gateway: docker-compose restart gateway" -ForegroundColor White
Write-Host "   3. Check logs: docker-compose logs gateway" -ForegroundColor White

Write-Host "`n"
