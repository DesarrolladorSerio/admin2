# Script para escanear vulnerabilidades en las imágenes del proyecto
# Requiere tener instalado Trivy (https://aquasecurity.github.io/trivy/)

$services = @(
    "auth-service-1",
    "reservations-service-1",
    "documents-service",
    "notifications-service",
    "datos-municipalidad-service",
    "frontend",
    "api-gateway",
    "auth-db",
    "reservations-db",
    "documents-db",
    "redis",
    "minio"
)

Write-Host "Iniciando escaneo de vulnerabilidades con Trivy..." -ForegroundColor Cyan

foreach ($service in $services) {
    Write-Host "Escaneando servicio: $service" -ForegroundColor Yellow
    # Se asume que las imágenes tienen el nombre del servicio o se construyen con docker-compose build
    # Este comando intenta escanear la imagen asociada al contenedor (si está corriendo o construida)
    
    # Obtener información de la imagen en formato JSON
    try {
        $imageInfoJson = docker-compose images --format json $service
        # Convertir JSON a objeto PowerShell
        # Nota: Si el comando falla o no devuelve JSON válido, caerá en el catch o $imageInfo será nulo
        $imageInfo = $imageInfoJson | ConvertFrom-Json
        
        if ($imageInfo) {
            # Si hay múltiples contenedores para el servicio, tomamos el primero
            if ($imageInfo -is [array]) {
                $imageInfo = $imageInfo[0]
            }
            
            $repo = $imageInfo.Repository
            $tag = $imageInfo.Tag
            
            if ($repo -and $tag) {
                $imageName = "$repo`:$tag"
                Write-Host "Imagen detectada: $imageName" -ForegroundColor Cyan
                # Ejecutar Trivy usando el nombre de la imagen (Repository:Tag)
                trivy image $imageName
            } else {
                Write-Host "No se pudo determinar el repositorio o tag para $service." -ForegroundColor Red
            }
        } else {
            Write-Host "No se encontró imagen para $service. Asegúrate de ejecutar 'docker-compose build' primero." -ForegroundColor Red
        }
    } catch {
        Write-Host "Error al procesar la imagen para $service. Detalles: $_" -ForegroundColor Red
    }
    Write-Host "---------------------------------------------------"
}
