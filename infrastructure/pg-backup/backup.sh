#!/usr/bin/env bash
set -euo pipefail

# Default retention 7 days if not set
: "${BACKUP_RETENTION_DAYS:=7}"

# Helper to timestamp
TODAY=$(date +%F)
BACKUP_DIR=/backups
mkdir -p "$BACKUP_DIR"

backup_db() {
  local host="$1" dbname="$2" user="$3" password="$4" prefix="$5"
  local outfile="${BACKUP_DIR}/backup_${prefix}_${TODAY}.sql"
  echo "[backup] Dumping ${dbname} from ${host} to ${outfile}"
  PGPASSWORD="$password" pg_dump -h "$host" -p 5432 -U "$user" -d "$dbname" -F p -f "$outfile"
}

# Perform backups for all three databases
backup_db "${AUTH_DB_HOST:-auth-db}" "${AUTH_DB_NAME:-auth_db}" "${AUTH_DB_USER:-admin}" "${AUTH_DB_PASSWORD:-admin}" "auth"
backup_db "${RES_DB_HOST:-reservations-db-primary}" "${RES_DB_NAME:-reservations_db}" "${RES_DB_USER:-admin}" "${RES_DB_PASSWORD:-admin}" "res"
backup_db "${DOC_DB_HOST:-documents-db}" "${DOC_DB_NAME:-documents_db}" "${DOC_DB_USER:-admin}" "${DOC_DB_PASSWORD:-admin}" "doc"

# Retention: delete older than BACKUP_RETENTION_DAYS
echo "[backup] Applying retention: keep last ${BACKUP_RETENTION_DAYS} days"
find "$BACKUP_DIR" -type f -name "backup_*.sql" -mtime +"$BACKUP_RETENTION_DAYS" -print -delete || true

# Upload to MinIO if bucket is set
if [[ -n "${MINIO_BUCKET:-}" ]]; then
  echo "[backup] Uploading backups to MinIO bucket: ${MINIO_BUCKET}"
  mc alias set minio "${MINIO_ENDPOINT:-http://minio:9000}" "${MINIO_ACCESS_KEY:-minioadmin}" "${MINIO_SECRET_KEY:-minioadmin}" >/dev/null 2>&1 || true
  mc mb --ignore-existing "minio/${MINIO_BUCKET}" >/dev/null 2>&1 || true
  mc cp --recursive --older-than 0d "${BACKUP_DIR}/" "minio/${MINIO_BUCKET}/" || true
fi

echo "[backup] Done at $(date -Is)"
