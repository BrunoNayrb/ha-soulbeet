# Soulbeet add-on documentation

This add-on repository and the Soulbeet fork it builds were written with AI assistance (xAI Grok). The behavior below is what the code does now. Paths are examples. Yours will be different.

## The two add-ons

**Soulbeet** runs the official app and adds the local database fix.

**Soulbeet Bulk** runs the fork. It has the database fix and CSV import.

The bulk add-on uses host port 9766 so it can run beside the original add-on on port 9765.

## Folders

Nothing in the fork assumes a particular disk layout.

- `download_path` and `music_base` are set on the add-on Configuration tab.
- The libraries themselves are added in the Soulbeet settings. Bulk import shows those libraries in a menu and sends downloads to the one you pick.
- Beets database files are redirected to `/data/beets_dbs/` on the Home Assistant disk. The music files stay where you put them.

| Path inside the add-on | Purpose |
|------------------------|---------|
| The download path you set | slskd downloads |
| Each library you add | Music files, and a bulk-import target |
| `/data/beets_dbs/` | Beets library databases |
| `/data/soulbeet.db` | Soulbeet application database |
| `/data/bulk_history.json` | Bulk import history |
| `/data/secret_key` | Web UI secret, created on first start |

## CSV import

```csv
title,album,artist
Alive,Ten,Pearl Jam
