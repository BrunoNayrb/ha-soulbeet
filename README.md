# Soulbeet Home Assistant Add-on

Custom Home Assistant add-on for [Soulbeet](https://github.com/terry90/soulbeet) — an automated music discovery and library manager that connects slskd (Soulseek) with beets.

This add-on is built for environments where the music library lives on a network share (CIFS/NFS). It forces all beets library databases onto local storage so imports no longer fail with “database is locked” errors.

## Features

- Latest Soulbeet (`:full` image) with AcoustID fingerprinting, cover art, lyrics, ReplayGain, and more
- Local beets databases (`/data/beets_dbs/`) to avoid CIFS locking issues
- Persistent configuration and data across updates
- Simple version-bump update flow through the Home Assistant UI
- Works with existing `/share` mounts

## Installation

1. Add this repository in the Home Assistant Add-on Store:
   https://github.com/bjguidry/ha-soulbeet
2. Refresh the repository.
3. Install **Soulbeet**.
4. Start the add-on and open the web UI on port **9765**.

## Configuration

In the add-on Configuration tab you can set:

| Option | Default | Description |
|--------|---------|-------------|
| `download_path` | `/share/Media/slskd/downloads` | Folder where slskd saves downloads (configurable) |
| `music_base` | `/share/Media/Music` | Base path for your music libraries (change in SoulBeets Settings) |
| `navidrome_url` | *(empty)* | Optional Navidrome URL for rating sync and playlists |

After starting, open the Soulbeet UI and:

- Add your music folders (e.g. `/share/Media/Music/Bryan`, `/share/Media/Music/Jeremiah`)
- Enter your slskd URL and API key
- Optionally connect Navidrome

## Updating

1. Change the `version` field in `config.yaml` to a higher value.
2. Commit and push.
3. In Home Assistant: Add-on Store → your repository → Reload.
4. Click **Update** on the Soulbeet add-on.

Settings, databases, and music files are preserved.

## Requirements

- Home Assistant OS / Supervised
- slskd running and reachable
- Music folders mounted under `/share` (or adjust the paths)
- Sufficient space on the add-on’s `/data` volume for the beets databases

## License

This add-on wrapper is provided as-is. Soulbeet itself is licensed under its own terms.
