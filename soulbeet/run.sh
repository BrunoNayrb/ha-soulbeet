#!/bin/bash
set -e

echo "[soulbeet] Starting HA add-on wrapper..."

# Persistent local storage for beets databases
mkdir -p /data/beets_dbs
chmod 755 /data /data/beets_dbs

# Generate or load SECRET_KEY
if [ ! -f /data/secret_key ]; then
  echo "[soulbeet] Generating new SECRET_KEY..."
  python3 -c "import secrets; print(secrets.token_urlsafe(48))" > /data/secret_key
  chmod 600 /data/secret_key
fi
export SECRET_KEY=$(cat /data/secret_key)

export DATABASE_URL="sqlite:/data/soulbeet.db"

# Parse HA options
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
if [ -n "$NAVIDROME_URL" ]; then
  export NAVIDROME_URL
fi

echo "[soulbeet] DOWNLOAD_PATH=${DOWNLOAD_PATH}"
echo "[soulbeet] MUSIC_BASE=${MUSIC_BASE}"
echo "[soulbeet] DATABASE_URL=${DATABASE_URL}"

# Install the beet wrapper that forces library DBs onto local storage.
# This is the reliable fix for CIFS/NFS SQLite locking.
REAL_BEET="/opt/venv/bin/beet.real"
WRAPPER="/opt/venv/bin/beet"

if [ ! -f "$REAL_BEET" ] && [ -f /opt/venv/bin/beet ]; then
  mv /opt/venv/bin/beet "$REAL_BEET"
fi

cat > "$WRAPPER" << 'EOF'
#!/bin/bash
# Wrapper that redirects any -l <path>/.beets_library.db to a local file
# under /data/beets_dbs/ so SQLite never touches the CIFS mount.

args=()
next_is_lib=0

for arg in "$@"; do
  if [ "$next_is_lib" = 1 ]; then
    if [[ "$arg" == *".beets_library.db" ]]; then
      parent=$(dirname "$arg")
      # Unique local name derived from the full parent path
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

exec /opt/venv/bin/beet.real "${args[@]}"
EOF

chmod 755 "$WRAPPER"

echo "[soulbeet] Beet wrapper installed. Library databases will be stored under /data/beets_dbs/"

# Optional: migrate any existing real .beets_library.db files from the share
# into the local location (best-effort).
if [ -d "$MUSIC_BASE" ]; then
  for libdir in "$MUSIC_BASE"/*/; do
    [ -d "$libdir" ] || continue
    name=$(basename "$libdir")
    [[ "$name" == .* ]] && continue
    src="${libdir}.beets_library.db"
    if [ -f "$src" ] && [ ! -L "$src" ]; then
      parent=$(dirname "$src")
      safe=$(echo "$parent" | sed 's|/|_|g' | sed 's|^_||' | sed 's|[^a-zA-Z0-9._-]|_|g')
      dest="/data/beets_dbs/${safe}.beets_library.db"
      if [ ! -f "$dest" ]; then
        echo "[soulbeet] Migrating existing DB: $src -> $dest"
        cp -a "$src" "$dest" || true
      fi
      # Leave the original; the wrapper will ignore it
    fi
  done
fi

echo "[soulbeet] Launching Soulbeet..."
if [ -x /app/server/server ]; then
  exec /app/server/server
elif [ -x /app/server/web ]; then
  exec /app/server/web
elif [ -x /app/server ]; then
  exec /app/server
else
  echo "[soulbeet] ERROR: Could not find Soulbeet server binary."
  ls -la /app/server || true
  exit 1
fi
