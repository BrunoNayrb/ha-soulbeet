# Base on a full Debian slim so we have a shell and package manager for the wrapper.
# Copy the application artifacts from the official Soulbeet image.
FROM python:3.11-slim-bookworm

# Install jq for parsing HA options
RUN apt-get update && apt-get install -y --no-install-recommends \
    jq \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy Soulbeet application and beets environment from the official image
COPY --from=docccccc/soulbeet:latest /app /app
COPY --from=docccccc/soulbeet:latest /opt/venv /opt/venv
COPY --from=docccccc/soulbeet:latest /opt/beets-plugins /opt/beets-plugins

# Environment matching the official image
ENV PATH="/opt/venv/bin:/usr/local/bin:$PATH"
ENV PYTHONPATH="/opt/venv/lib/python3.11/site-packages"
ENV DATABASE_URL="sqlite:/data/soulbeet.db"
ENV PORT=9765
ENV IP=0.0.0.0
ENV HOME=/tmp

WORKDIR /app

# Copy our startup wrapper
COPY run.sh /run.sh
RUN chmod a+x /run.sh

EXPOSE 9765

ENTRYPOINT ["/run.sh"]
