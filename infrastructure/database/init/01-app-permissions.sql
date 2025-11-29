-- Create application user
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'app_user') THEN

      CREATE USER app_user WITH PASSWORD 'AppUserPass456!Secure';
   END IF;
END
$do$;

-- Revoke default permissions
REVOKE ALL ON SCHEMA public FROM public;
REVOKE ALL ON SCHEMA public FROM app_user;

-- Grant usage on schema
GRANT USAGE ON SCHEMA public TO app_user;

-- Grant specific permissions on all tables (future tables too)
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;

-- Grant usage on sequences (for serial IDs)
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO app_user;
