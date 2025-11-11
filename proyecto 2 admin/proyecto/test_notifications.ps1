# Script de prueba para el servicio de notificaciones
# Ejecutar después de levantar los servicios con docker-compose

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  PRUEBA DEL SERVICIO DE NOTIFICACIONES" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# 1. Health Check
Write-Host "1️⃣  Verificando health del servicio..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8004/health" -Method Get
    Write-Host "✅ Servicio de notificaciones: " -NoNewline
    Write-Host $health.status -ForegroundColor Green
    Write-Host "   Redis: $($health.redis)" -ForegroundColor Gray
}
catch {
    Write-Host "❌ Error: El servicio no está disponible" -ForegroundColor Red
    Write-Host "   Asegúrate de ejecutar: docker-compose up -d notifications-service" -ForegroundColor Yellow
    exit 1
}

# 2. Obtener token de prueba
Write-Host "`n2️⃣  Obteniendo token de autenticación..." -ForegroundColor Yellow
$loginBody = @{
    username = "admin"
    password = "admin"
} | ConvertTo-Json

try {
    $loginResponse = Invoke-RestMethod -Uri "http://localhost/api/auth/token" -Method Post -Body $loginBody -ContentType "application/json"
    $token = $loginResponse.access_token
    Write-Host "✅ Token obtenido exitosamente" -ForegroundColor Green
}
catch {
    Write-Host "⚠️  No se pudo obtener token, continuando sin autenticación..." -ForegroundColor Yellow
    $token = $null
}

# 3. Enviar email de prueba
Write-Host "`n3️⃣  Enviando email de prueba..." -ForegroundColor Yellow
$emailBody = @{
    to_emails = @("test@example.com")
    subject   = "Test desde Script PowerShell"
    html_body = "<h1>✅ ¡Funciona!</h1><p>El servicio de notificaciones está operativo.</p><p>Enviado el $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')</p>"
} | ConvertTo-Json

try {
    $headers = @{
        "Content-Type" = "application/json"
    }
    if ($token) {
        $headers["Authorization"] = "Bearer $token"
    }
    
    $response = Invoke-RestMethod -Uri "http://localhost/api/notifications/email" -Method Post -Body $emailBody -Headers $headers
    Write-Host "✅ Email encolado exitosamente" -ForegroundColor Green
    Write-Host "   Task ID: $($response.task_id)" -ForegroundColor Gray
    Write-Host "   Status: $($response.status)" -ForegroundColor Gray
    
    $taskId = $response.task_id
    
    # 4. Consultar estado de la tarea
    Write-Host "`n4️⃣  Consultando estado de la tarea..." -ForegroundColor Yellow
    Start-Sleep -Seconds 2
    
    try {
        $taskStatus = Invoke-RestMethod -Uri "http://localhost/api/notifications/task/$taskId" -Method Get -Headers $headers
        Write-Host "✅ Estado de la tarea:" -ForegroundColor Green
        Write-Host "   Task ID: $($taskStatus.task_id)" -ForegroundColor Gray
        Write-Host "   Status: $($taskStatus.status)" -ForegroundColor Gray
        
        if ($taskStatus.status -eq "SUCCESS") {
            Write-Host "   ✅ Email enviado correctamente" -ForegroundColor Green
        }
        elseif ($taskStatus.status -eq "PENDING" -or $taskStatus.status -eq "STARTED") {
            Write-Host "   ⏳ Email en proceso de envío..." -ForegroundColor Yellow
        }
        elseif ($taskStatus.status -eq "FAILURE") {
            Write-Host "   ❌ Error al enviar email" -ForegroundColor Red
        }
    }
    catch {
        Write-Host "⚠️  No se pudo consultar el estado de la tarea" -ForegroundColor Yellow
    }
    
}
catch {
    Write-Host "❌ Error al enviar email" -ForegroundColor Red
    Write-Host "   $($_.Exception.Message)" -ForegroundColor Red
}

# 5. Probar notificación de reserva (simulada)
Write-Host "`n5️⃣  Enviando notificación de reserva simulada..." -ForegroundColor Yellow
$reservationBody = @{
    user_email       = "usuario@example.com"
    user_name        = "Usuario de Prueba"
    reservation_data = @{
        id       = 999
        date     = (Get-Date).ToString("yyyy-MM-dd")
        time     = "10:00"
        service  = "Licencia de Conducir"
        location = "Oficina Principal"
    }
} | ConvertTo-Json

try {
    $headers = @{
        "Content-Type" = "application/json"
    }
    if ($token) {
        $headers["Authorization"] = "Bearer $token"
    }
    
    $response = Invoke-RestMethod -Uri "http://localhost/api/notifications/reservation/confirmation" -Method Post -Body $reservationBody -Headers $headers
    Write-Host "✅ Notificación de reserva encolada" -ForegroundColor Green
    Write-Host "   Task ID: $($response.task_id)" -ForegroundColor Gray
}
catch {
    Write-Host "❌ Error al enviar notificación de reserva" -ForegroundColor Red
}

# 6. Obtener estadísticas
Write-Host "`n6️⃣  Obteniendo estadísticas del servicio..." -ForegroundColor Yellow
try {
    $stats = Invoke-RestMethod -Uri "http://localhost/api/notifications/stats" -Method Get
    Write-Host "✅ Estadísticas:" -ForegroundColor Green
    Write-Host "   Servicio: $($stats.service)" -ForegroundColor Gray
    Write-Host "   Redis conectado: $($stats.redis_connected)" -ForegroundColor Gray
    Write-Host "   Timestamp: $($stats.timestamp)" -ForegroundColor Gray
}
catch {
    Write-Host "⚠️  No se pudieron obtener estadísticas" -ForegroundColor Yellow
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  ✅ PRUEBAS COMPLETADAS" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "⚠️  IMPORTANTE:" -ForegroundColor Yellow
Write-Host "   Para que los emails se envíen realmente, configura en .env:" -ForegroundColor Yellow
Write-Host "   SMTP_USER=tu-email@gmail.com" -ForegroundColor Gray
Write-Host "   SMTP_PASSWORD=tu-contraseña-de-aplicacion`n" -ForegroundColor Gray

Write-Host "📝 Comandos útiles:" -ForegroundColor Cyan
Write-Host "   Ver logs del servicio:" -ForegroundColor White
Write-Host "   docker-compose logs -f notifications-service`n" -ForegroundColor Gray
Write-Host "   Ver logs del worker:" -ForegroundColor White
Write-Host "   docker-compose logs -f celery-worker`n" -ForegroundColor Gray
Write-Host "   Consultar Redis:" -ForegroundColor White
Write-Host "   docker exec -it redis_queue redis-cli`n" -ForegroundColor Gray
# Script de prueba para el servicio de notificaciones
# Ejecutar después de levantar los servicios con docker-compose

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  PRUEBA DEL SERVICIO DE NOTIFICACIONES" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# 1. Health Check
Write-Host "1️⃣  Verificando health del servicio..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8004/health" -Method Get
    Write-Host "✅ Servicio de notificaciones: " -NoNewline
    Write-Host $health.status -ForegroundColor Green
    Write-Host "   Redis: $($health.redis)" -ForegroundColor Gray
}
catch {
    Write-Host "❌ Error: El servicio no está disponible" -ForegroundColor Red
    Write-Host "   Asegúrate de ejecutar: docker-compose up -d notifications-service" -ForegroundColor Yellow
    exit 1
}

# 2. Obtener token de prueba
Write-Host "`n2️⃣  Obteniendo token de autenticación..." -ForegroundColor Yellow
$loginBody = @{
    username = "admin"
    password = "admin"
} | ConvertTo-Json

try {
    $loginResponse = Invoke-RestMethod -Uri "http://localhost/api/auth/token" -Method Post -Body $loginBody -ContentType "application/json"
    $token = $loginResponse.access_token
    Write-Host "✅ Token obtenido exitosamente" -ForegroundColor Green
}
catch {
    Write-Host "⚠️  No se pudo obtener token, continuando sin autenticación..." -ForegroundColor Yellow
    $token = $null
}

# 3. Enviar email de prueba
Write-Host "`n3️⃣  Enviando email de prueba..." -ForegroundColor Yellow
$emailBody = @{
    to_emails = @("test@example.com")
    subject   = "Test desde Script PowerShell"
    html_body = "<h1>✅ ¡Funciona!</h1><p>El servicio de notificaciones está operativo.</p><p>Enviado el $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')</p>"
} | ConvertTo-Json

try {
    $headers = @{
        "Content-Type" = "application/json"
    }
    if ($token) {
        $headers["Authorization"] = "Bearer $token"
    }
    
    $response = Invoke-RestMethod -Uri "http://localhost/api/notifications/email" -Method Post -Body $emailBody -Headers $headers
    Write-Host "✅ Email encolado exitosamente" -ForegroundColor Green
    Write-Host "   Task ID: $($response.task_id)" -ForegroundColor Gray
    Write-Host "   Status: $($response.status)" -ForegroundColor Gray
    
    $taskId = $response.task_id
    
    # 4. Consultar estado de la tarea
    Write-Host "`n4️⃣  Consultando estado de la tarea..." -ForegroundColor Yellow
    Start-Sleep -Seconds 2
    
    try {
        $taskStatus = Invoke-RestMethod -Uri "http://localhost/api/notifications/task/$taskId" -Method Get -Headers $headers
        Write-Host "✅ Estado de la tarea:" -ForegroundColor Green
        Write-Host "   Task ID: $($taskStatus.task_id)" -ForegroundColor Gray
        Write-Host "   Status: $($taskStatus.status)" -ForegroundColor Gray
        
        if ($taskStatus.status -eq "SUCCESS") {
            Write-Host "   ✅ Email enviado correctamente" -ForegroundColor Green
        }
        elseif ($taskStatus.status -eq "PENDING" -or $taskStatus.status -eq "STARTED") {
            Write-Host "   ⏳ Email en proceso de envío..." -ForegroundColor Yellow
        }
        elseif ($taskStatus.status -eq "FAILURE") {
            Write-Host "   ❌ Error al enviar email" -ForegroundColor Red
        }
    }
    catch {
        Write-Host "⚠️  No se pudo consultar el estado de la tarea" -ForegroundColor Yellow
    }
    
}
catch {
    Write-Host "❌ Error al enviar email" -ForegroundColor Red
    Write-Host "   $($_.Exception.Message)" -ForegroundColor Red
}

# 5. Probar notificación de reserva (simulada)
Write-Host "`n5️⃣  Enviando notificación de reserva simulada..." -ForegroundColor Yellow
$reservationBody = @{
    user_email       = "usuario@example.com"
    user_name        = "Usuario de Prueba"
    reservation_data = @{
        id       = 999
        date     = (Get-Date).ToString("yyyy-MM-dd")
        time     = "10:00"
        service  = "Licencia de Conducir"
        location = "Oficina Principal"
    }
} | ConvertTo-Json

try {
    $headers = @{
        "Content-Type" = "application/json"
    }
    if ($token) {
        $headers["Authorization"] = "Bearer $token"
    }
    
    $response = Invoke-RestMethod -Uri "http://localhost/api/notifications/reservation/confirmation" -Method Post -Body $reservationBody -Headers $headers
    Write-Host "✅ Notificación de reserva encolada" -ForegroundColor Green
    Write-Host "   Task ID: $($response.task_id)" -ForegroundColor Gray
}
catch {
    Write-Host "❌ Error al enviar notificación de reserva" -ForegroundColor Red
}

# 6. Obtener estadísticas
Write-Host "`n6️⃣  Obteniendo estadísticas del servicio..." -ForegroundColor Yellow
try {
    $stats = Invoke-RestMethod -Uri "http://localhost/api/notifications/stats" -Method Get
    Write-Host "✅ Estadísticas:" -ForegroundColor Green
    Write-Host "   Servicio: $($stats.service)" -ForegroundColor Gray
    Write-Host "   Redis conectado: $($stats.redis_connected)" -ForegroundColor Gray
    Write-Host "   Timestamp: $($stats.timestamp)" -ForegroundColor Gray
}
catch {
    Write-Host "⚠️  No se pudieron obtener estadísticas" -ForegroundColor Yellow
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  ✅ PRUEBAS COMPLETADAS" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "⚠️  IMPORTANTE:" -ForegroundColor Yellow
Write-Host "   Para que los emails se envíen realmente, configura en .env:" -ForegroundColor Yellow
Write-Host "   SMTP_USER=tu-email@gmail.com" -ForegroundColor Gray
Write-Host "   SMTP_PASSWORD=tu-contraseña-de-aplicacion`n" -ForegroundColor Gray

Write-Host "📝 Comandos útiles:" -ForegroundColor Cyan
Write-Host "   Ver logs del servicio:" -ForegroundColor White
Write-Host "   docker-compose logs -f notifications-service`n" -ForegroundColor Gray
Write-Host "   Ver logs del worker:" -ForegroundColor White
Write-Host "   docker-compose logs -f celery-worker`n" -ForegroundColor Gray
Write-Host "   Consultar Redis:" -ForegroundColor White
Write-Host "   docker exec -it redis_queue redis-cli`n" -ForegroundColor Gray
