# Build Soulbeet from the fork
FROM rust:latest AS builder
RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*
RUN git clone --depth 1 https://github.com/BrunoNayrb/soulbeet.git /src
WORKDIR /src
RUN cargo build --release --features server

# Runtime (based on your working add-on)
FROM python:3.11-slim-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends \
    jq \
    ca-certificates \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy beets environment from the official image
COPY --from=docccccc/soulbeet:full /opt/venv /opt/venv
COPY --from=docccccc/soulbeet:full /opt/beets-plugins /opt/beets-plugins

# Copy the binary we just built
# See what binaries were built
RUN find /src/target/release -type f -executable -not -name "*.d" -not -name "*.rlib" -ls || true
RUN ls -la /src/target/release/ || true

# Adjust this line once we know the real binary name
# COPY --from=builder /src/target/release/SOMETHING /app/server

ENV PATH="/opt/venv/bin:/usr/local/bin:$PATH"
ENV PYTHONPATH="/opt/venv/lib/python3.11/site-packages"
ENV DATABASE_URL="sqlite:/data/soulbeet.db"
ENV PORT=9765
ENV IP=0.0.0.0
ENV HOME=/tmp
ENV BEETS_PYTHON=/opt/venv/bin/python
WORKDIR /app

# Startup script with the DB redirect wrapper
RUN cat > /run.sh << 'EOF'
#!/bin/bash
set -e
echo "[soulbeet] Starting HA add-on wrapper..."
mkdir -p /data/beets_dbs
chmod 755 /data /data/beets_dbs
if [ ! -f /data/secret_key ]; then
  echo "[soulbeet] Generating new SECRET_KEY..."
  python3 -c "import secrets; print(secrets.token_urlsafe(48))" > /data/secret_key
  chmod 600 /data/secret_key
fi
export SECRET_KEY=$(cat /data/secret_key)
export DATABASE_URL="sqlite:/data/soulbeet.db"
CONFIG_PATH="/data/options.json"
if [ -f "$CONFIG_PATH" ]; then
  DOWNLOAD_PATH=$(jq -r '.download_path // "/share/Media/slskd/downloads"' "$CONFIG_PATH")
  MUSIC_BASE=$(jq -r '.music_base // "/share/Media/Music"' "$CONFIG_PATH")
  NAVIDROME_URL=$(jq -r '.navidrome_url // empty' "$CONFIG_PATH")
else
  DOWNLOAD_PATH="/share/Media/slskd/downloads"
  MUSIC_BASE="/share/Media/Music"
  NAVIDROME_URL=""
fi
export DOWNLOAD_PATH
[ -n "$NAVIDROME_URL" ] && export NAVIDROME_URL
echo "[soulbeet] DOWNLOAD_PATH=${DOWNLOAD_PATH}"
echo "[soulbeet] MUSIC_BASE=${MUSIC_BASE}"

# Python wrapper that redirects library DB paths
PYTHON_WRAPPER="/opt/venv/bin/python-wrapper"
cat > "$PYTHON_WRAPPER" << 'PYWRAP'
#!/bin/bash
echo "[python-wrapper] Called with: $*" >&2
args=()
for arg in "$@"; do
  if [[ "$arg" == *".beets_library.db" ]]; then
    parent=$(dirname "$arg")
    safe=$(echo "$parent" | sed 's|/|_|g' | sed 's|^_||' | sed 's|[^a-zA-Z0-9._-]|_|g')
    local_db="/data/beets_dbs/${safe}.beets_library.db"
    echo "[python-wrapper] Redirecting library DB: $arg -> $local_db" >&2
    args+=("$local_db")
  else
    args+=("$arg")
  fi
done
exec /opt/venv/bin/python "${args[@]}"
PYWRAP
chmod 755 "$PYTHON_WRAPPER"
export BEETS_PYTHON="$PYTHON_WRAPPER"
echo "[soulbeet] BEETS_PYTHON set to wrapper: $BEETS_PYTHON" >&2
echo "[soulbeet] Launching Soulbeet..."
exec /app/server
EOF
RUN chmod a+x /run.sh

EXPOSE 9765
ENTRYPOINT ["/run.sh"]
