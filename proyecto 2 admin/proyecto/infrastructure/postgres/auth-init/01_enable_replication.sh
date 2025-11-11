#!/bin/bash
set -e

# Configura pg_hba.conf para permitir únicamente replicación desde la subred interna
# definida en docker-compose para database_net (172.28.0.0/16), usando scram-sha-256.

PGDATA_DIR=${PGDATA:-/var/lib/postgresql/data}
echo "[auth-init] Habilitando replicación segura desde 172.28.0.0/16 (md5)"
echo "host replication replicator 172.28.0.0/16 md5" >> "$PGDATA_DIR/pg_hba.conf"
echo "host all ${AUTH_DB_USER} 0.0.0.0/0 md5" >> "$PGDATA_DIR/pg_hba.conf"

# Asegurar que Postgres escuche en todas las interfaces dentro del contenedor
echo "listen_addresses = '*'" >> "$PGDATA_DIR/postgresql.conf"

# Forzar cifrado moderno para contraseñas
echo "password_encryption = 'scram-sha-256'" >> "$PGDATA_DIR/postgresql.conf"

echo "[auth-init] Configuración de replicación aplicada."
