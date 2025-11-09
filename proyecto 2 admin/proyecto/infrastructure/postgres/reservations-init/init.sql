-- Init SQL for reservations DB: create replication role
CREATE ROLE replicator WITH REPLICATION LOGIN PASSWORD 'replica_pass';
