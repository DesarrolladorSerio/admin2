#!/bin/bash
set -e

# Configura pg_hba.conf para permitir replicación solo desde la subred interna
# definida en docker-compose para database_net (172.28.0.0/16), usando scram-sha-256.

PGDATA_DIR=${PGDATA:-/var/lib/postgresql/data}
echo "[reservations-init] Habilitando replicación segura desde 172.28.0.0/16 (md5)"
echo "host replication replicator 172.28.0.0/16 md5" >> "$PGDATA_DIR/pg_hba.conf"
echo "host all ${RESERVATIONS_DB_USER} 0.0.0.0/0 md5" >> "$PGDATA_DIR/pg_hba.conf"

# Escuchar en todas las interfaces del contenedor
echo "listen_addresses = '*'" >> "$PGDATA_DIR/postgresql.conf"

# Asegurar cifrado moderno de contraseñas
echo "password_encryption = 'scram-sha-256'" >> "$PGDATA_DIR/postgresql.conf"

echo "[reservations-init] Configuración de replicación aplicada."
