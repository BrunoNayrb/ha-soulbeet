# Build from your fork using the official method
FROM rust:1.99-bookworm AS builder
ARG CACHEBUST=2
RUN apt-get update && apt-get install -y --no-install-recommends \
    git pkg-config libssl-dev curl \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

RUN cargo install dioxus-cli@0.7.4 --locked

WORKDIR /src
RUN git clone --depth 1 https://github.com/BrunoNayrb/soulbeet.git .
RUN npm install
RUN npx @tailwindcss/cli -i ./web/assets/input.css -o ./web/assets/tailwind.css

# Force a clean bundle so Docker doesn't reuse a bad cache
RUN rm -rf /src/target
RUN dx bundle --package web --release

# Runtime
FROM python:3.11-slim-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends \
    jq ca-certificates ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Beets environment from official image
COPY --from=docccccc/soulbeet:full /opt/venv /opt/venv
COPY --from=docccccc/soulbeet:full /opt/beets-plugins /opt/beets-plugins
COPY --from=docccccc/soulbeet:full /app/beets_config.yaml /app/beets_config.yaml

# Binary + assets from the dx bundle
COPY --from=builder /src/target/dx/web/release/web /app/server

ENV PATH="/opt/venv/bin:/usr/local/bin:$PATH"
ENV PYTHONPATH="/opt/venv/lib/python3.11/site-packages"
ENV DATABASE_URL="sqlite:/data/soulbeet.db"
ENV PORT=9765
ENV IP=0.0.0.0
ENV HOME=/tmp
ENV BEETS_PYTHON=/opt/venv/bin/python
WORKDIR /app

# Startup script with DB redirect wrapper
RUN cat > /run.sh << 'EOF'
#!/bin/bash
set -e
echo "[soulbeet] Starting HA add-on wrapper..."
mkdir -p /data/beets_dbs
chmod 755 /data /data/beets_dbs
if [ ! -f /data/secret_key ]; then
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
echo "[soulbeet] NAVIDROME_URL=${NAVIDROME_URL:-not set}"

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
echo "[soulbeet] Launching Soulbeet..."

# Try the most likely binary names inside the bundle directory
if [ -x /app/server/web ]; then
  exec /app/server/web
elif [ -x /app/server/server ]; then
  exec /app/server/server
else
  echo "[soulbeet] ERROR: binary not found in /app/server"
  ls -la /app/server || true
  exit 1
fi
EOF
RUN chmod a+x /run.sh

EXPOSE 9765
ENTRYPOINT ["/run.sh"]
