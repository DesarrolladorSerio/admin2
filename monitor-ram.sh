#!/bin/bash

# Script de monitoreo de uso de RAM en Docker Compose
# Uso: ./monitor-ram.sh [intervalo_segundos]

INTERVAL=${1:-5}  # Intervalo por defecto: 5 segundos

echo "🔍 Monitoreando uso de RAM de contenedores Docker"
echo "📊 Intervalo: ${INTERVAL} segundos"
echo "⏹️  Presiona Ctrl+C para detener"
echo ""
echo "=========================================="

while true; do
    clear
    echo "📅 $(date '+%Y-%m-%d %H:%M:%S')"
    echo "=========================================="
    echo ""
    
    # Mostrar estadísticas ordenadas por uso de memoria
    docker stats --no-stream --format "table {{.Name}}\t{{.MemUsage}}\t{{.MemPerc}}\t{{.CPUPerc}}" | \
        head -n 1
    
    docker stats --no-stream --format "table {{.Name}}\t{{.MemUsage}}\t{{.MemPerc}}\t{{.CPUPerc}}" | \
        tail -n +2 | \
        sort -k3 -hr
    
    echo ""
    echo "=========================================="
    
    # Calcular uso total aproximado
    TOTAL_MEM=$(docker stats --no-stream --format "{{.MemUsage}}" | \
        awk '{split($1,a,/[A-Za-z]/); sum+=a[1]; if($1 ~ /GiB/) sum+=a[1]*1024-a[1]} END {printf "%.2f", sum}')
    
    echo "💾 Uso total aproximado: ${TOTAL_MEM} MiB"
    echo ""
    
    # Servicios que más consumen
    echo "🔥 Top 5 consumidores de RAM:"
    docker stats --no-stream --format "{{.Name}}: {{.MemUsage}}" | \
        sort -t: -k2 -hr | \
        head -5 | \
        nl
    
    echo ""
    echo "⏳ Próxima actualización en ${INTERVAL} segundos..."
    
    sleep $INTERVAL
done
