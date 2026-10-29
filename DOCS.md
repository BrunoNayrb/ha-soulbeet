# Soulbeet Add-on Documentation

## Overview

This add-on runs Soulbeet inside Home Assistant and solves the common “database is locked” problem that occurs when beets tries to store its SQLite library file on a CIFS/NFS share.

All beets library databases are redirected to local storage (`/data/beets_dbs/`) while the actual music files remain on your shared storage.

## Image Tier

The add-on is built from the official `docccccc/soulbeet:full` image, which includes:

- MusicBrainz tagging
- AcoustID / chroma fingerprinting
- Cover art fetching and embedding
- Lyrics
- Last.fm genres
- ReplayGain
- Tag scrubbing and other convenience plugins

## How the local database fix works

Soulbeet normally creates a `.beets_library.db` file inside each music folder. On a network share this frequently causes SQLite locking errors.

The add-on installs a small wrapper around the `beet` command. Whenever Soulbeet passes a library path ending in `.beets_library.db`, the wrapper rewrites it to a safe local path under `/data/beets_dbs/`. The music files themselves are untouched.

## Folder layout

| Path | Purpose |
|------|---------|
| `/share/Media/slskd/downloads` | slskd download directory (configurable) |
| `/share/Media/Music/...` | Your music libraries (added in the Soulbeet UI) |
| `/data/beets_dbs/` | Local beets library databases (managed automatically) |
| `/data/soulbeet.db` | Soulbeet’s own application database |
| `/data/secret_key` | Generated secret for the web UI |

## Environment variables

The following are set automatically:

- `BEETS_PYTHON=/opt/venv/bin/python` — required for the full image
- `DATABASE_URL=sqlite:/data/soulbeet.db`
- `SECRET_KEY` — generated on first run and stored in `/data`

## Updating Soulbeet

The add-on uses the floating `:full` tag. To pull a newer Soulbeet release:

1. Increment `version` in `config.yaml`.
2. Push the change.
3. Reload the repository in Home Assistant.
4. Click Update.

No data is lost.

## Troubleshooting

### “database is locked”
- Confirm the add-on is using the local-database wrapper (check the start log for `[beet-wrapper]` messages).
- Make sure you are not manually placing `.beets_library.db` files on the network share.

### “BEETS MISSING” or “Cannot determine the Python”
- Ensure `ENV BEETS_PYTHON=/opt/venv/bin/python` is present in the Dockerfile.
- Rebuild/reinstall the add-on.

### ReplayGain warning
- The Dockerfile must install `ffmpeg`. The current version already does this.

### Poor matching / non-English albums
- The full image includes AcoustID fingerprinting, which greatly improves matching on poorly tagged Soulseek downloads.
- You can re-import problem albums with `beet import -t` for stricter matching.

## Custom beets configuration

To override the default beets config, mount or copy a `config.yaml` and set the `BEETS_CONFIG` environment variable to its path. Most users can leave the defaults alone.

## Support

This is an unofficial add-on. For Soulbeet application issues see the upstream project. For add-on specific problems (database location, wrapper, HA integration), open an issue in this repository.
