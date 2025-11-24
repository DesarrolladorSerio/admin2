#!/bin/bash
# Script para optimizar WSL2 y Docker Desktop

echo "🚀 Optimizando configuración de WSL2 y Docker..."

# Verificar si existe el archivo .wslconfig en el directorio home del usuario de Windows
WSLCONFIG_PATH="/mnt/c/Users/$USER/.wslconfig"

# Crear o actualizar .wslconfig
echo "📝 Configurando límites de WSL2..."
cat > "$WSLCONFIG_PATH" << 'EOF'
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
EOF

echo "✅ Archivo .wslconfig actualizado en: $WSLCONFIG_PATH"

echo "🔄 Para aplicar los cambios:"
echo "1. Ejecuta: wsl --shutdown"
echo "2. Reinicia Docker Desktop"
echo "3. Ejecuta: docker compose up -d --build"

echo ""
echo "📊 Resumen de optimizaciones aplicadas:"
echo "• WSL2 limitado a 6GB de RAM (de tus 12GB totales)"
echo "• Procesadores limitados a 4 cores"
echo "• Todos los contenedores tienen límites de memoria individuales:"
echo "  - Bases de datos principales: 128MB cada una"
echo "  - Bases de datos réplica: 64MB cada una"
echo "  - Servicios de aplicación: 256MB cada uno"
echo "  - Ollama (IA): 2GB (el más pesado)"
echo "  - Servicios de monitoreo: 32-256MB cada uno"
echo "• Total estimado de RAM de Docker: ~4-5GB máximo"

echo ""
echo "⚠️  IMPORTANTE: Después de ejecutar estos comandos, reinicia tu PC para asegurar que todos los cambios se apliquen correctamente."