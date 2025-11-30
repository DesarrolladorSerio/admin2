#!/bin/bash
set -e

# Read password from secret file
if [ -f /run/secrets/app_user_password ]; then
    APP_USER_PASSWORD=$(cat /run/secrets/app_user_password)
else
    echo "Secret file /run/secrets/app_user_password not found!"
    exit 1
fi

# Create application user
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    DO
    \$do\$
    BEGIN
       IF NOT EXISTS (
          SELECT FROM pg_catalog.pg_roles
          WHERE  rolname = 'app_user') THEN

          CREATE USER app_user WITH PASSWORD '$APP_USER_PASSWORD';
       ELSE
          ALTER USER app_user WITH PASSWORD '$APP_USER_PASSWORD';
       END IF;
    END
    \$do\$;

    -- Revoke default permissions
    REVOKE ALL ON SCHEMA public FROM public;
    REVOKE ALL ON SCHEMA public FROM app_user;

    -- Grant usage and create on schema
    GRANT USAGE, CREATE ON SCHEMA public TO app_user;
    
    -- Grant privileges on all tables and sequences (future proofing)
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO app_user;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO app_user;
EOSQL
