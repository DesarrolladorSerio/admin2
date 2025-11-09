#!/bin/bash
set -euo pipefail

# Replica entrypoint: wait for primary, perform base backup and start as standby
# Expected env vars:
# PRIMARY_HOST, PRIMARY_PORT, REPLICATION_USER, REPLICATION_PASSWORD,
# POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB

PGDATA=${PGDATA:-/var/lib/postgresql/data}

# If DB already initialized, just run default entrypoint
if [ -f "$PGDATA/PG_VERSION" ]; then
  echo "PGDATA already initialized, starting postgres"
  exec docker-entrypoint.sh postgres
fi

: "Waiting for primary to be ready..."
PRIMARY_PORT=${PRIMARY_PORT:-5432}
until pg_isready -h "$PRIMARY_HOST" -p "$PRIMARY_PORT" -U "$REPLICATION_USER" >/dev/null 2>&1; do
  echo "Waiting for primary $PRIMARY_HOST:$PRIMARY_PORT..."
  sleep 1
done

echo "Performing base backup from primary..."
# Ensure pg_basebackup can authenticate using PGPASSFILE
export PGPASSFILE=$(mktemp)
echo "$PRIMARY_HOST:$PRIMARY_PORT:*:$REPLICATION_USER:$REPLICATION_PASSWORD" > "$PGPASSFILE"
chmod 0600 "$PGPASSFILE"

# Clean any existing data just in case
rm -rf "$PGDATA"/*

pg_basebackup -h "$PRIMARY_HOST" -p "$PRIMARY_PORT" -D "$PGDATA" -U "$REPLICATION_USER" -v -P --wal-method=stream

# Configure standby
echo "primary_conninfo = 'host=${PRIMARY_HOST} port=${PRIMARY_PORT} user=${REPLICATION_USER} password=${REPLICATION_PASSWORD}'" >> "$PGDATA/postgresql.conf"
# Create standby signal (Postgres 12+)
touch "$PGDATA/standby.signal"

chown -R postgres:postgres "$PGDATA"

rm -f "$PGPASSFILE"

echo "Starting postgres in standby mode"
exec docker-entrypoint.sh postgres
