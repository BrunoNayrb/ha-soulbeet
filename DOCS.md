# Soulbeet Add-on Documentation

Soulbeet is a self-hosted music downloader and organizer that bridges **slskd** (Soulseek) and **beets**.

This add-on packages the official Docker image and solves the common problem of SQLite locking when the beets library databases live on a CIFS-mounted RAID.

## Configuration options

| Option | Default | Description |
|--------|---------|-------------|
| `download_path` | `/share/Media/slskd/downloads` | Path (inside the container) where slskd writes downloads. Must be the same physical location that your slskd add-on/container uses. |
| `music_base` | `/share/Media/Music` | Base directory containing your music libraries. Every immediate subfolder gets a local beets database via symlink. |
| `navidrome_url` | *(empty)* | Optional URL of your Navidrome instance (for discovery playlists and rating sync). |

## First-time setup

1. Make sure the `/share/Media` CIFS mount is available and writable by the add-on.
2. Start the add-on.
3. Open `http://<ha-ip>:9765` (or the ingress/port mapping you configured).
4. Create an account in the web UI.
5. Go to Settings and:
   - Enter your slskd URL and API key.
   - Confirm the download path.
6. Add music folders:
   - `/share/Media/Music/Bryan`
   - `/share/Media/Music/Jeremiah`
7. Start searching and downloading. Imports will use the local databases and should no longer lock.

## Troubleshooting

- **Database still locks**: Confirm the symlink exists (`ls -l /share/Media/Music/Bryan/.beets_library.db` should show a link pointing into `/data/beets_dbs/`). Restart the add-on after adding new library folders so the startup script can create the symlink.
- **Cannot see downloads**: Verify the download path is identical between slskd and this add-on, and that both can read/write it.
- **Permission errors**: The add-on runs as root by default; ensure the CIFS mount allows writes from the HAOS host.

Local data (Soulbeet DB, secret key, beets DBs) lives in the add-on's data directory and survives updates.
