# Paperless-ngx Tag Sync (Filename-based)

📄 Utility script for **Paperless-ngx**, which scans configured directories
(e.g. `PLATNE`, `NEPLATNE`, `ZRUSENE`) and updates tags of matching documents
in Paperless-ngx **based on filename match**.

> ⚠️ This version does **not** use checksums – pairing is done by filename
(`original_filename` or `title` stem). Good enough for setups where API
does not expose checksum.

---

## Features

- [x] Walks directories (e.g. on SMB mount).
- [x] Matches documents in Paperless by filename.
- [x] Assigns target tags (`PLATNE`, `NEPLATNE`, `ZRUSENE`).
- [x] Dry-run mode (`--apply` to actually change).
- [x] Verbose output with current and desired tags.

---

## Usage

### 1. Configure `.env`

```ini
# Paperless
PAPERLESS_BASE_URL=http://paperless:8000
PAPERLESS_API_TOKEN=REPLACE_ME

# Directories to scan
PLATNE_DIR=/mnt/nas/DOC/PLATNE
NEPLATNE_DIR=/mnt/nas/DOC/NEPLATNE
ZRUSENE_DIR=/mnt/nas/DOC/ZRUSENE

# Search mode: only filename (no checksum available in API)
SEARCH_MODE=filename

## Run the sync
python ./bin/dir_sync.py --verbose --limit 20
python /bin/dir_sync.py --apply
Options:

--apply : actually PATCHes tags (default is dry-run).

--verbose : show current/final tag sets.

--limit N : process max N files (for testing).




## Example output
=== PLATNE: /mnt/nas/DOC/PLATNE
[CHG ] id= 962  D-C-E155-20080801.doc  -> Platné  (match=filename)
[OK  ] id= 542  P330-C-20251007_Priloha_3.pdf (tags OK, match=filename)
[MISS] P055-V-20231007_Priloha_5.docx -> NOT in Paperless (import first)

--- SUMMARY ---
Files scanned      : 23
Found in Paperless : 16
Would change       : 8
Not in Paperless   : 4
Matched by filename: 16
