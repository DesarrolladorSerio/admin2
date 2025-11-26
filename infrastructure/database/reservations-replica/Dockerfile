FROM postgres:16.4

# Security: Run vulnerability scan with: trivy image <image-name>

# Copy a small entrypoint that will initialize this container as a streaming replica
COPY replica-entrypoint.sh /usr/local/bin/replica-entrypoint.sh
RUN chmod +x /usr/local/bin/replica-entrypoint.sh \
    && chown postgres:postgres /usr/local/bin/replica-entrypoint.sh

# Switch to non-privileged user
USER postgres

ENTRYPOINT ["/usr/local/bin/replica-entrypoint.sh"]
CMD ["postgres"]
