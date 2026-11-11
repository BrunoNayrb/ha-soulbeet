# Soulbeet Home Assistant add-ons

Two Home Assistant add-ons for [Soulbeet](https://github.com/BrunoNayrb/soulbeet), a Soulseek downloader and library manager that uses slskd and beets.

| Add-on | What it is | Web UI |
|--------|------------|--------|
| Soulbeet | Official Soulbeet app with the local database fix | Port 9765 |
| Soulbeet Bulk | Custom fork with CSV import | Port 9766 |

Both can be installed together. Music stays on the network share. The beets library databases are stored on the Home Assistant disk so imports do not fail with "database is locked".

## Soulbeet Bulk

Built from the [BrunoNayrb/soulbeet](https://github.com/BrunoNayrb/soulbeet) fork.

- Paste a CSV with the columns `title,album,artist`. The first line is skipped.
- Each song is searched as an album first, then as a single track if that fails.
- Live, concert, acoustic, demo, and similar recordings are skipped.
- Matches are queued into `/share/Media/Music/Bryan`.
- The page lists every row. Queued rows are kept, and failed rows have a **Search album** button that opens Search with the artist and album filled in.
- The list is saved and survives a refresh. **Clear history** removes it.
- A long list no longer dies with a gateway timeout. Rows show as working, then queued or failed.

The finished image is built on GitHub and published to `ghcr.io/brunonayrb/soulbeet-bulk`. Home Assistant downloads that image.

## Soulbeet

The original add-on runs the official Soulbeet image and adds the same local database fix. It does not include CSV import.

## Installation

1. In the Home Assistant add-on store, add `https://github.com/BrunoNayrb/ha-soulbeet`.
2. Reload the repository.
3. Install **Soulbeet Bulk**, **Soulbeet**, or both.
4. Start the add-on and open its web UI.

On the Configuration tab:

| Option | Default | Description |
|--------|---------|-------------|
| `download_path` | `/share/Media/slskd/downloads` | Folder where slskd saves downloads |
| `music_base` | `/share/Media/Music` | Parent folder of the libraries |
| `navidrome_url` | empty | Navidrome address, if login should use Navidrome |

In the Soulbeet UI, add the library folders and the slskd address and API key.

## Updating Soulbeet Bulk

1. Push the code changes to [BrunoNayrb/soulbeet](https://github.com/BrunoNayrb/soulbeet).
2. Raise `version` in `soulbeet-bulk/config.yaml` and commit it.
3. Wait until the GitHub Action is green.
4. Reload the repository in Home Assistant and press **Update**.

Settings, the import history, and the beets databases stay in place.
