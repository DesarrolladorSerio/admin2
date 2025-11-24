#!/bin/bash
set -e

# Este script se ejecuta antes del inicio de PostgreSQL
# Añade las reglas de replicación a pg_hba.conf

echo "🔧 Configurando pg_hba.conf para replicación..."

# Agregar regla para replicación si no existe
if ! grep -q "host replication replicator" "${PGDATA}/pg_hba.conf" 2>/dev/null; then
    echo "host replication replicator 0.0.0.0/0 trust" >> "${PGDATA}/pg_hba.conf"
    echo "✅ Regla de replicación agregada"
else
    echo "ℹ️  Regla de replicación ya existe"
fi

# Ejecutar el entrypoint original de postgres
exec docker-entrypoint.sh "$@"
