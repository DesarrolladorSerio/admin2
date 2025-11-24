# Script PowerShell para optimizar WSL2 y Docker Desktop
# Ejecutar como Administrador

Write-Host "Optimizando configuracion de WSL2 y Docker..." -ForegroundColor Green

# Obtener el directorio home del usuario
$UserProfile = $env:USERPROFILE
$WslConfigPath = "$UserProfile\.wslconfig"

Write-Host "Configurando limites de WSL2..." -ForegroundColor Yellow

# Crear contenido del archivo .wslconfig
$WslConfigContent = @"
[wsl2]
# Limita la memoria de WSL2 a 6GB (ajusta según tu sistema)
memory=6GB

# Limita el procesamiento a 4 cores (ajusta según tu CPU)  
processors=4

# Limita el swap
swap=2GB

# Habilita nested virtualization (opcional)
nestedVirtualization=true

# Configuración de localización
localhostForwarding=true

# Configuraciones adicionales de rendimiento
pageReporting=true
kernelCommandLine=cgroup_no_v1=all systemd.unified_cgroup_hierarchy=1
"@

# Escribir el archivo
$WslConfigContent | Out-File -FilePath $WslConfigPath -Encoding UTF8

Write-Host "Archivo .wslconfig actualizado en: $WslConfigPath" -ForegroundColor Green

Write-Host ""
Write-Host "Aplicando cambios automaticamente..." -ForegroundColor Yellow

# Detener WSL
Write-Host "Deteniendo WSL..." -ForegroundColor Blue
wsl --shutdown
Start-Sleep -Seconds 3

# Verificar si Docker Desktop está ejecutándose
$dockerProcess = Get-Process -Name "Docker Desktop" -ErrorAction SilentlyContinue

if ($dockerProcess) {
    Write-Host "Reiniciando Docker Desktop..." -ForegroundColor Blue
    Stop-Process -Name "Docker Desktop" -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 5
    
    # Intentar iniciar Docker Desktop (buscar en ubicaciones comunes)
    $dockerPaths = @(
        "$env:ProgramFiles\Docker\Docker\Docker Desktop.exe",
        "${env:ProgramFiles(x86)}\Docker\Docker\Docker Desktop.exe",
        "$env:LOCALAPPDATA\Programs\Docker\Docker Desktop.exe"
    )
    
    foreach ($path in $dockerPaths) {
        if (Test-Path $path) {
            Start-Process -FilePath $path
            Write-Host "Docker Desktop iniciado desde: $path" -ForegroundColor Green
            break
        }
    }
    
    Write-Host "Esperando que Docker Desktop inicie completamente..." -ForegroundColor Blue
    Start-Sleep -Seconds 15
}

Write-Host ""
Write-Host "Resumen de optimizaciones aplicadas:" -ForegroundColor Cyan
Write-Host "- WSL2 limitado a 6GB de RAM (de tus 12GB totales)" -ForegroundColor White
Write-Host "- Procesadores limitados a 4 cores" -ForegroundColor White
Write-Host "- Todos los contenedores tienen limites de memoria individuales:" -ForegroundColor White
Write-Host "  * Bases de datos principales: 128MB cada una" -ForegroundColor Gray
Write-Host "  * Bases de datos replica: 64MB cada una" -ForegroundColor Gray
Write-Host "  * Servicios de aplicacion: 256MB cada uno" -ForegroundColor Gray
Write-Host "  * Ollama (IA): 2GB (el mas pesado)" -ForegroundColor Gray
Write-Host "  * Servicios de monitoreo: 32-256MB cada uno" -ForegroundColor Gray
Write-Host "- Total estimado de RAM de Docker: ~4-5GB maximo" -ForegroundColor White

Write-Host ""
Write-Host "Ahora puedes ejecutar:" -ForegroundColor Green
Write-Host "docker compose up -d --build" -ForegroundColor Yellow

Write-Host ""
Write-Host "NOTA: Si experimentas problemas, reinicia tu PC completamente." -ForegroundColor Red