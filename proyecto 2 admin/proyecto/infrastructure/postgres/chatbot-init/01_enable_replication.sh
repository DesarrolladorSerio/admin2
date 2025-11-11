#!/bin/bash
# Script para habilitar replicación en PostgreSQL (ChatBot DB)

set -e

# Configurar postgresql.conf para replicación
cat >> ${PGDATA}/postgresql.conf <<EOF

# Replication Settings
wal_level = replica
max_wal_senders = 10
max_replication_slots = 10
hot_standby = on
EOF

# Configurar pg_hba.conf para permitir conexiones de replicación
echo "host replication replicator 0.0.0.0/0 md5" >> ${PGDATA}/pg_hba.conf

# Crear usuario de replicación si no existe
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'replicator') THEN
            CREATE ROLE replicator WITH REPLICATION PASSWORD '${REPLICATION_PASSWORD}' LOGIN;
        END IF;
    END
    \$\$;
EOSQL

echo "Replicación habilitada para ChatBot DB"
