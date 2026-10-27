# Soulbeet HAOS Add-on

Home Assistant add-on for [Soulbeet](https://github.com/terry90/soulbeet) (latest version).

## Key fixes for this build

- Soulbeet application database (`soulbeet.db`) is stored locally under the add-on's `/data` directory.
- Beets library databases (`.beets_library.db`) are stored locally and symlinked into each music library folder under your music base path. This avoids SQLite file-locking failures that commonly occur on CIFS/NFS mounts when importing between folders.

## Paths (defaults matching your setup)

- Downloads: `/share/Media/slskd/downloads`
- Music libraries: `/share/Media/Music/Bryan` and `/share/Media/Music/Jeremiah` (any subfolder under `/share/Media/Music` gets a local DB symlink automatically)

## Installation

1. Place this `soulbeet-addon` folder inside your existing HA add-on repository on GitHub.
2. In Home Assistant: Settings → Add-ons → Add-on Store → ⋮ → Repositories → add your GitHub repo URL.
3. Install the **Soulbeet** add-on.
4. Configure options if needed (download path / music base / optional Navidrome URL).
5. Start the add-on.
6. Open the Web UI on port **9765** (or via the add-on page).
7. In the Soulbeet UI, add your music folders using the **exact** container paths:
   - `/share/Media/Music/Bryan`
   - `/share/Media/Music/Jeremiah`
8. Set the download path in Soulbeet settings to match `DOWNLOAD_PATH` (default `/share/Media/slskd/downloads`).

## Notes

- Requires a running **slskd 0.26 or newer** that Soulbeet can reach (configure the URL + API key in the Soulbeet web UI).
- The `/share` folder is mounted read-write so Soulbeet can move files from downloads into your libraries.
- On first start a secure `SECRET_KEY` is generated and stored in `/data/secret_key`.
- If you previously had `.beets_library.db` files on the CIFS share, the startup script will migrate them to local storage and replace them with symlinks.
- To use the `:medium` or `:full` image (more beets plugins), edit the `FROM` line in the `Dockerfile` and rebuild/update the add-on.

## Updating

When a new Soulbeet release is out, change the image tag in the `Dockerfile` (or keep `:latest`) and update the add-on version in `config.yaml`, then rebuild.
