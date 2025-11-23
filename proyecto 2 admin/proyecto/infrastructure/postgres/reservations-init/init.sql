-- Init SQL for reservations DB: create replication role
CREATE ROLE replicator WITH REPLICATION LOGIN PASSWORD 'replica_pass';

-- Configurar parámetros de replicación
ALTER SYSTEM SET wal_level = 'replica';
ALTER SYSTEM SET max_wal_senders = 3;
ALTER SYSTEM SET max_replication_slots = 3;
ALTER SYSTEM SET hot_standby = on;

-- Recargar configuración (requiere reinicio para wal_level)
SELECT pg_reload_conf();
