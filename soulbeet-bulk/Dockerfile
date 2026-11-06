# Build from your fork
FROM rust:1.81-bookworm AS builder
RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*
RUN git clone --depth 1 https://github.com/BrunoNayrb/soulbeet.git /src
WORKDIR /src
RUN cargo build --release -p api

# Runtime
FROM python:3.11-slim-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends \
    jq \
    ca-certificates \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /src/target/release/api /app/server

# Minimal startup script
RUN cat > /run.sh << 'EOF'
#!/bin/sh
set -e
mkdir -p /data
export DATABASE_URL="sqlite:/data/soulbeet.db"
export DOWNLOAD_PATH="${DOWNLOAD_PATH:-/share/Media/slskd/downloads}"
export HOME=/tmp
exec /app/server
EOF
RUN chmod a+x /run.sh

ENV PATH="/usr/local/bin:$PATH"
EXPOSE 9765
ENTRYPOINT ["/run.sh"]
