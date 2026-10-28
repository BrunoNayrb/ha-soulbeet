# Base on a full Debian slim so we have a shell and package manager for the wrapper.
# Copy the application artifacts from the official Soulbeet image.
FROM python:3.11-slim-bookworm

# Install jq for parsing HA options
RUN apt-get update && apt-get install -y --no-install-recommends \
    jq \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy Soulbeet application and beets environment from the official image
COPY --from=docccccc/soulbeet:full /app /app
COPY --from=docccccc/soulbeet:full /opt/venv /opt/venv
COPY --from=docccccc/soulbeet:full /opt/beets-plugins /opt/beets-plugins

# Environment matching the official image
ENV PATH="/opt/venv/bin:/usr/local/bin:$PATH"
ENV PYTHONPATH="/opt/venv/lib/python3.11/site-packages"
ENV DATABASE_URL="sqlite:/data/soulbeet.db"
ENV PORT=9765
ENV IP=0.0.0.0
ENV HOME=/tmp
ENV BEETS_PYTHON=/opt/venv/bin/python

WORKDIR /app

# Create the startup script inside the image (includes the fixed beet wrapper)
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

# Install beet wrapper that forces library DBs onto local storage
REAL_BEET="/opt/venv/bin/beet.real"
WRAPPER="/opt/venv/bin/beet"
if [ ! -f "$REAL_BEET" ] && [ -x /opt/venv/bin/beet ]; then
  mv /opt/venv/bin/beet "$REAL_BEET"
fi

cat > "$WRAPPER" << 'INNER'
#!/bin/bash
args=()
next_is_lib=0
for arg in "$@"; do
  if [ "$next_is_lib" = 1 ]; then
    if [[ "$arg" == *".beets_library.db" ]]; then
      parent=$(dirname "$arg")
      safe=$(echo "$parent" | sed 's|/|_|g' | sed 's|^_||' | sed 's|[^a-zA-Z0-9._-]|_|g')
      local_db="/data/beets_dbs/${safe}.beets_library.db"
      echo "[beet-wrapper] Redirecting library DB: $arg -> $local_db" >&2
      args+=("$local_db")
    else
      args+=("$arg")
    fi
    next_is_lib=0
  elif [ "$arg" = "-l" ]; then
    args+=("-l")
    next_is_lib=1
  else
    args+=("$arg")
  fi
done
# Explicit Python so a broken shebang cannot fail
exec /opt/venv/bin/python /opt/venv/bin/beet.real "${args[@]}"
INNER
chmod 755 "$WRAPPER"
echo "[soulbeet] Beet wrapper installed (local DBs under /data/beets_dbs)"

echo "[soulbeet] Launching Soulbeet..."
if [ -x /app/server/server ]; then
  exec /app/server/server
elif [ -x /app/server/web ]; then
  exec /app/server/web
elif [ -x /app/server ]; then
  exec /app/server
else
  echo "[soulbeet] ERROR: server binary not found"
  ls -la /app/server || true
  exit 1
fi
EOF
RUN chmod a+x /run.sh

EXPOSE 9765
ENTRYPOINT ["/run.sh"]
