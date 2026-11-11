# Soulbeet Home Assistant add-ons

Two Home Assistant add-ons for a fork of Soulbeet, a Soulseek downloader and library manager that uses slskd and beets.

This fork and these add-on files were written with AI assistance (xAI Grok) and checked by hand. It is a personal project. Expect rough edges, and read the code before you rely on it.

| Add-on | What it is | Web UI |
|--------|------------|--------|
| Soulbeet | Official Soulbeet app with the local database fix | Port 9765 |
| Soulbeet Bulk | This fork, including CSV import | Port 9766 |

Both can be installed together. Music stays wherever you mount it. The beets library databases are stored on the Home Assistant disk so imports do not fail with "database is locked".

## Soulbeet Bulk

Source: [BrunoNayrb/soulbeet](https://github.com/BrunoNayrb/soulbeet)

- Paste a CSV with the columns `title,album,artist`. The first line is skipped.
- Choose which library receives the downloads. The list is the folders you added in Soulbeet, not a fixed path.
- Each song is searched as an album first, then as a single track if that fails.
- Live, concert, acoustic, demo, and similar recordings are skipped.
- The page lists every row. Failed rows have a **Search album** button that opens Search with the artist and album filled in.
- The list is saved and survives a refresh. **Clear history** removes it.

The image is built on GitHub and published to `ghcr.io/brunonayrb/soulbeet-bulk`. Home Assistant downloads that image.

## Installation

1. In the Home Assistant add-on store, add `https://github.com/BrunoNayrb/ha-soulbeet`.
2. Reload the repository.
3. Install **Soulbeet Bulk**, **Soulbeet**, or both.
4. On the Configuration tab, set your own folders. The defaults are empty on purpose.

| Option | What to enter |
|--------|----------------|
| `download_path` | The folder where slskd saves downloads |
| `music_base` | The parent folder of your libraries |
| `navidrome_url` | Your Navidrome address, or leave it empty |

Then start the add-on, open the web UI, and add each library folder there. Bulk import can only send music to a folder that has been added.

## Updating Soulbeet Bulk

1. Push the code changes to the soulbeet fork.
2. Raise `version` in `soulbeet-bulk/config.yaml` and commit it.
3. Wait until the GitHub Action is green.
4. Reload the repository in Home Assistant and press **Update**.

Settings, the import history, and the beets databases stay in place.
