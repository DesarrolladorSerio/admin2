# Script de monitoreo de uso de RAM en Docker Compose (PowerShell)
# Uso: .\monitor-ram.ps1 [-Interval 5]

param(
    [int]$Interval = 5  # Intervalo por defecto: 5 segundos
)

Write-Host "🔍 Monitoreando uso de RAM de contenedores Docker" -ForegroundColor Cyan
Write-Host "📊 Intervalo: $Interval segundos" -ForegroundColor Cyan
Write-Host "⏹️  Presiona Ctrl+C para detener" -ForegroundColor Yellow
Write-Host ""
Write-Host "==========================================" -ForegroundColor Green

function Get-DockerStats {
    $stats = docker stats --no-stream --format "{{.Name}}|{{.MemUsage}}|{{.MemPerc}}|{{.CPUPerc}}"
    
    $statsArray = @()
    foreach ($line in $stats) {
        $parts = $line -split '\|'
        if ($parts.Length -eq 4) {
            $memUsage = $parts[1] -replace '\s*/\s*.*', ''  # Solo la parte usada
            $memPerc = $parts[2] -replace '%', ''
            
            $statsArray += [PSCustomObject]@{
                Name = $parts[0]
                MemUsage = $memUsage
                MemPerc = [double]$memPerc
                CPUPerc = $parts[3]
            }
        }
    }
    
    return $statsArray | Sort-Object -Property MemPerc -Descending
}

function Format-MemorySize {
    param([string]$MemString)
    
    if ($MemString -match '(\d+\.?\d*)\s*([A-Za-z]+)') {
        $value = [double]$matches[1]
        $unit = $matches[2]
        
        switch ($unit) {
            'GiB' { return $value * 1024 }
            'MiB' { return $value }
            'KiB' { return $value / 1024 }
            default { return $value }
        }
    }
    return 0
}

try {
    while ($true) {
        Clear-Host
        
        Write-Host "📅 $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan
        Write-Host "==========================================" -ForegroundColor Green
        Write-Host ""
        
        $stats = Get-DockerStats
        
        # Encabezado
        Write-Host ("{0,-30} {1,-15} {2,-10} {3,-10}" -f "NOMBRE", "USO RAM", "RAM %", "CPU %") -ForegroundColor Yellow
        Write-Host ("{0,-30} {1,-15} {2,-10} {3,-10}" -f "------", "-------", "-----", "-----") -ForegroundColor DarkGray
        
        # Datos
        foreach ($stat in $stats) {
            $color = "White"
            if ($stat.MemPerc -gt 80) { $color = "Red" }
            elseif ($stat.MemPerc -gt 60) { $color = "Yellow" }
            elseif ($stat.MemPerc -gt 40) { $color = "Cyan" }
            
            Write-Host ("{0,-30} {1,-15} {2,-10} {3,-10}" -f `
                $stat.Name, `
                $stat.MemUsage, `
                "$($stat.MemPerc.ToString('0.00'))%", `
                $stat.CPUPerc) -ForegroundColor $color
        }
        
        Write-Host ""
        Write-Host "==========================================" -ForegroundColor Green
        
        # Calcular uso total
        $totalMem = 0
        foreach ($stat in $stats) {
            $totalMem += Format-MemorySize -MemString $stat.MemUsage
        }
        
        Write-Host "💾 Uso total aproximado: $($totalMem.ToString('0.00')) MiB" -ForegroundColor Magenta
        Write-Host ""
        
        # Top 5 consumidores
        Write-Host "🔥 Top 5 consumidores de RAM:" -ForegroundColor Red
        $top5 = $stats | Select-Object -First 5
        $counter = 1
        foreach ($item in $top5) {
            Write-Host "  $counter. $($item.Name): $($item.MemUsage) ($($item.MemPerc.ToString('0.00'))%)" -ForegroundColor White
            $counter++
        }
        
        Write-Host ""
        Write-Host "⏳ Próxima actualización en $Interval segundos..." -ForegroundColor DarkGray
        
        Start-Sleep -Seconds $Interval
    }
}
catch {
    Write-Host ""
    Write-Host "❌ Error: $_" -ForegroundColor Red
    Write-Host "Asegúrate de que Docker esté ejecutándose." -ForegroundColor Yellow
}
finally {
    Write-Host ""
    Write-Host "👋 Monitoreo detenido." -ForegroundColor Green
}
