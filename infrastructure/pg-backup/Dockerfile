# Lightweight image with pg_dump available and busybox crond
FROM postgres:16-alpine

# Security: Run vulnerability scan with: trivy image <image-name>

# Install tools: curl (for downloading mc), bash, tzdata
RUN apk add --no-cache bash curl ca-certificates tzdata && update-ca-certificates

# Install MinIO client (mc)
RUN curl -fsSL https://dl.min.io/client/mc/release/linux-amd64/mc -o /usr/local/bin/mc \
    && chmod +x /usr/local/bin/mc

# Create app directory
WORKDIR /app

# Copy scripts
COPY backup.sh /app/backup.sh
COPY restore-db.sh /app/restore-db.sh
COPY entrypoint.sh /app/entrypoint.sh

RUN chmod +x /app/*.sh \
    && mkdir -p /backups \
    && chown -R postgres:postgres /app /backups

# Switch to non-privileged user
USER postgres

# Run entrypoint which installs the cron job from BACKUP_SCHEDULE and runs crond in foreground
ENTRYPOINT ["/app/entrypoint.sh"]
