#!/usr/bin/env bash
set -euo pipefail

# Usage: restore-db.sh <db_host> <db_name> <db_user> <db_password> [path_to_sql]
# If path_to_sql not provided, it restores from the most recent backup_<prefix>_YYYY-MM-DD.sql

HOST=${1:-}
DB=${2:-}
USER=${3:-}
PASS=${4:-}
FILE=${5:-}

if [[ -z "$HOST" || -z "$DB" || -z "$USER" || -z "$PASS" ]]; then
  echo "Usage: $0 <db_host> <db_name> <db_user> <db_password> [sql_file]"
  exit 1
fi

# Determine prefix from db name
PREFIX="unknown"
case "$DB" in
  auth_*) PREFIX="auth";;
  reservations_*|reservations_db) PREFIX="res";;
  documents_*|documents_db) PREFIX="doc";;
  *) PREFIX="${DB}";;
 esac

if [[ -z "${FILE}" ]]; then
  FILE=$(ls -1t /backups/backup_${PREFIX}_*.sql 2>/dev/null | head -n1 || true)
fi

if [[ ! -f "$FILE" ]]; then
  echo "[restore] No backup file found for prefix ${PREFIX}"
  exit 1
fi

echo "[restore] Restoring ${DB} on ${HOST} from ${FILE}"
PGPASSWORD="$PASS" psql -h "$HOST" -p 5432 -U "$USER" -d "$DB" -f "$FILE"

echo "[restore] Done"
