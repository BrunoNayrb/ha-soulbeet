# Soulbeet add-on documentation

## The two add-ons

**Soulbeet** runs the official app. Its only local change is the beets database fix.

**Soulbeet Bulk** runs the custom fork. It has the database fix plus CSV import.

The bulk add-on listens on port 9766 so it can run beside the original add-on on port 9765.

## CSV import

Use a file like this:

```csv
title,album,artist
Alive,Ten,Pearl Jam
