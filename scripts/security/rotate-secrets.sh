#!/bin/bash

# scripts/security/rotate-secrets.sh

SECRETS_DIR="./infrastructure/secrets"
mkdir -p "$SECRETS_DIR"

echo "Rotating secrets..."

# Function to generate a random secret
generate_secret() {
    openssl rand -hex 32
}

# Rotate DB Password
echo "Rotating DB Password..."
generate_secret > "$SECRETS_DIR/db_password.txt"

# Rotate App User Password
echo "Rotating App User Password..."
generate_secret > "$SECRETS_DIR/app_user_password.txt"

# Rotate JWT Secret
echo "Rotating JWT Secret..."
generate_secret > "$SECRETS_DIR/jwt_secret.txt"

# Rotate MinIO Keys
echo "Rotating MinIO Keys..."
# MinIO Access Key (usually shorter, alphanumeric)
openssl rand -hex 8 > "$SECRETS_DIR/minio_access_key.txt"
# MinIO Secret Key
openssl rand -hex 32 > "$SECRETS_DIR/minio_secret_key.txt"

echo "Secrets rotated successfully on $(date)"
echo "Restarting services to apply changes..."

docker compose down
docker compose up -d

echo "Services restarted."
