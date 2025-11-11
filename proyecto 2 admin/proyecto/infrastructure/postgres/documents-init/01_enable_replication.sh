#!/bin/bash
set -e

# Configura pg_hba.conf para permitir replicación solo desde la subred interna
# definida en docker-compose para database_net (172.28.0.0/16), usando scram-sha-256.

PGDATA_DIR=${PGDATA:-/var/lib/postgresql/data}
echo "[documents-init] Habilitando replicación segura desde 172.28.0.0/16 (scram-sha-256)"
echo "host replication replicator 172.28.0.0/16 scram-sha-256" >> "$PGDATA_DIR/pg_hba.conf"

# Escuchar en todas las interfaces del contenedor
echo "listen_addresses = '*'" >> "$PGDATA_DIR/postgresql.conf"

# Asegurar cifrado moderno de contraseñas
echo "password_encryption = 'scram-sha-256'" >> "$PGDATA_DIR/postgresql.conf"

echo "[documents-init] Configuración de replicación aplicada."
