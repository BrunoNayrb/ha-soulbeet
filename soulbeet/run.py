#!/bin/bash
set -e

echo "[soulbeet] Starting HA add-on wrapper..."

# Persistent data directory (local to HAOS)
mkdir -p /data/beets_dbs
chmod 755 /data /data/beets_dbs

# Generate or load SECRET_KEY
if [ ! -f /data/secret_key ]; then
  echo "[soulbeet] Generating new SECRET_KEY..."
  python3 -c "import secrets; print(secrets.token_urlsafe(48))" > /data/secret_key
  chmod 600 /data/secret_key
fi
export SECRET_KEY=$(cat /data/secret_key)

# Soulbeet application database (always local)
export DATABASE_URL="sqlite:/data/soulbeet.db"

# Parse options from HA
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

# Ensure download directory is accessible
if [ ! -d "$DOWNLOAD_PATH" ]; then
  echo "[soulbeet] WARNING: Download path ${DOWNLOAD_PATH} does not exist or is not mounted."
fi

# Set up local beets databases via symlinks for all music libraries under MUSIC_BASE
# This avoids SQLite locking problems on CIFS/NFS mounts.
if [ -d "$MUSIC_BASE" ]; then
  echo "[soulbeet] Setting up local beets databases for libraries under ${MUSIC_BASE}..."
  for libdir in "$MUSIC_BASE"/*/; do
    if [ -d "$libdir" ]; then
      name=$(basename "$libdir")
      # Skip if name is empty or starts with .
      if [ -z "$name" ] || [[ "$name" == .* ]]; then
        continue
      fi
      local_db="/data/beets_dbs/${name}.beets_library.db"
      target_db="${libdir}.beets_library.db"

      # If a real (non-symlink) DB exists on the network share, move it locally
      if [ -e "$target_db" ] && [ ! -L "$target_db" ]; then
        echo "[soulbeet] Migrating existing DB for ${name} to local storage..."
        mv "$target_db" "$local_db" || true
      fi

      # Create/update the symlink
      ln -sfn "$local_db" "$target_db"
      echo "[soulbeet] Linked ${target_db} -> ${local_db}"
    fi
  done
else
  echo "[soulbeet] WARNING: Music base ${MUSIC_BASE} not found. Add libraries later and restart the add-on to create DB symlinks."
fi

echo "[soulbeet] Launching Soulbeet..."
# The official image places the server binary at /app/server/server
# (Dioxus fullstack release layout). Fall back if needed.
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
