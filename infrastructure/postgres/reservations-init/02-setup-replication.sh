#!/bin/bash
# Script para configurar replicación de PostgreSQL - Reservations DB

set -e

# Configurar pg_hba.conf para permitir replicación desde cualquier red
echo "host replication replicator 172.28.0.0/16 trust" >> /var/lib/postgresql/data/pg_hba.conf
echo "host replication replicator all trust" >> /var/lib/postgresql/data/pg_hba.conf

# Configurar postgresql.conf para replicación
cat >> /var/lib/postgresql/data/postgresql.conf <<EOF

# Configuración de replicación
wal_level = replica
max_wal_senders = 3
max_replication_slots = 3
hot_standby = on
EOF

# Recargar configuración
pg_ctl reload -D /var/lib/postgresql/data || true

echo "✅ Configuración de replicación completada para Reservations DB"
