FROM minio/minio:latest AS source

FROM alpine:latest

# Update OS and install dependencies
RUN apk update && apk upgrade --no-cache && \
    apk add --no-cache ca-certificates curl

# Copy binaries from official image
COPY --from=source /usr/bin/minio /usr/bin/minio
COPY --from=source /usr/bin/mc /usr/bin/mc

# Create user and group
RUN addgroup -S minio && adduser -S minio -G minio

# Create data directory
RUN mkdir /data && chown minio:minio /data

# Switch to user
USER minio

# Set entrypoint
ENTRYPOINT ["/usr/bin/minio"]
CMD ["server", "/data"]
