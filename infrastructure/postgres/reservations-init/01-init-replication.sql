-- Init SQL for reservations DB
-- Crear rol de replicación
CREATE ROLE replicator WITH REPLICATION LOGIN PASSWORD 'replica_pass';

-- Configurar PostgreSQL para replicación usando ALTER SYSTEM
ALTER SYSTEM SET wal_level = 'replica';
ALTER SYSTEM SET max_wal_senders = 3;
ALTER SYSTEM SET max_replication_slots = 3;
ALTER SYSTEM SET hot_standby = on;
ALTER SYSTEM SET listen_addresses = '*';

-- Nota: pg_hba.conf debe configurarse manualmente o con script posterior
-- Las siguientes líneas deben agregarse a pg_hba.conf:
-- host replication replicator 172.28.0.0/16 md5
-- host replication replicator all trust
-- host all ${RESERVATIONS_DB_USER} 0.0.0.0/0 md5
