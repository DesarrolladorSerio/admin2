#!/bin/bash
set -e

PGDATA_DIR=${PGDATA:-/var/lib/postgresql/data}

echo "[chatbot-init] Copiando configuración pg_hba.conf predefinida..."
cp /docker-entrypoint-initdb.d/pg_hba.conf.template "$PGDATA_DIR/pg_hba.conf"

echo "[chatbot-init] Configurando PostgreSQL..."
# Usar ALTER SYSTEM es más seguro que modificar archivos directamente
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Configurar PostgreSQL
    ALTER SYSTEM SET wal_level = 'replica';
    ALTER SYSTEM SET max_wal_senders = 10;
    ALTER SYSTEM SET max_replication_slots = 10;
    ALTER SYSTEM SET hot_standby = on;
    ALTER SYSTEM SET listen_addresses = '*';
    
    -- Crear usuario de replicación si no existe
    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'replicator') THEN
            CREATE ROLE replicator WITH REPLICATION PASSWORD '\${REPLICATION_PASSWORD}' LOGIN;
        END IF;
    END
    \$\$;
EOSQL

echo "[chatbot-init] Configuración completada. Reiniciando PostgreSQL..."
pg_ctl reload -D "$PGDATA_DIR" || true
