#!/bin/bash
set -e

PGDATA_DIR=${PGDATA:-/var/lib/postgresql/data}

echo "[auth-init] Copiando configuración pg_hba.conf predefinida..."
cp /docker-entrypoint-initdb.d/pg_hba.conf.template "$PGDATA_DIR/pg_hba.conf"

echo "[auth-init] Configurando PostgreSQL para replicación..."
# Usar ALTER SYSTEM es más seguro que modificar archivos directamente
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Configurar PostgreSQL para replicación
    ALTER SYSTEM SET wal_level = 'replica';
    ALTER SYSTEM SET max_wal_senders = 3;
    ALTER SYSTEM SET max_replication_slots = 3;
    ALTER SYSTEM SET hot_standby = on;
    ALTER SYSTEM SET listen_addresses = '*';
    
    -- Crear usuario de replicación
    CREATE ROLE replicator WITH REPLICATION LOGIN PASSWORD 'replica_pass';
EOSQL

echo "[auth-init] Configuración completada. Reiniciando PostgreSQL..."
pg_ctl reload -D "$PGDATA_DIR" || true
