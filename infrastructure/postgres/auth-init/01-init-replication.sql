-- Init SQL for auth DB
-- Crear rol de replicación
CREATE ROLE replicator WITH REPLICATION LOGIN PASSWORD 'replica_pass';

-- Configurar pg_hba.conf para replicación
-- Nota: se configura mediante el script 02-setup-replication.sh
