import argparse, sys
from pathlib import Path
from .config import (PLATNE_DIR, NEPLATNE_DIR, ZRUSENE_DIR, SEARCH_MODE)
from .fs import iter_files, sha256_file
from .finder import find_doc_resilient
from .tags import get_all_tags, compute_final_tag_ids
from .http import http_patch
from .http import http_get

def _target_for_label(label: str, cfg) -> str:
    # import zde kvůli lazy importu (aby se config nahrál předem)
    from .config import TAG_VALID, TAG_EXPIRED, TAG_CANCELLED
    if label == "PLATNE":   return TAG_VALID
    if label == "NEPLATNE": return TAG_EXPIRED
    if label == "ZRUSENE":  return TAG_CANCELLED
    return None

def _set_doc_tags(doc_id: int, new_tag_ids: set, apply_changes: bool):
    if not apply_changes:
        print(f"[DRY] Would PATCH /documents/{doc_id} tags -> {sorted(new_tag_ids)}")
        return
    http_patch(f"/api/documents/{doc_id}/", {"tags": sorted(list(new_tag_ids))})
    print(f"[OK ] Updated doc {doc_id} tags -> {sorted(new_tag_ids)}")

def run_dir_sync():
    ap = argparse.ArgumentParser(description="Paperless tag sync (directories). Default is DRY-RUN.")
    ap.add_argument("--limit", type=int, default=0, help="Max files to process (0=all).")
    ap.add_argument("--apply", action="store_true", help="Apply changes (otherwise DRY-RUN).")
    ap.add_argument("--verbose", action="store_true", help="Print current/final tag sets.")
    args = ap.parse_args()

    match_checksum = 0
    match_filename = 0

    id_to_name, name_to_id = get_all_tags()

    to_scan = []
    if PLATNE_DIR:   to_scan.append((PLATNE_DIR, "PLATNE"))
    if NEPLATNE_DIR: to_scan.append((NEPLATNE_DIR, "NEPLATNE"))
    if ZRUSENE_DIR:  to_scan.append((ZRUSENE_DIR, "ZRUSENE"))

    if not to_scan:
        print("ERROR: Configure PLATNE_DIR/NEPLATNE_DIR in .env", file=sys.stderr)
        sys.exit(2)

    total = found = changed = misses = 0

    for root, label in to_scan:
        target_name = _target_for_label(label, None)
        print(f"\n=== {label}: {root}")
        for fpath in iter_files(root):
            total += 1
            if args.limit and total > args.limit:
                break

            try:
                checksum = sha256_file(fpath)
            except Exception as e:
                print(f"[ERR ] Hash failed: {fpath} ({e})")
                continue

            doc, method = find_doc_resilient(fpath, checksum, SEARCH_MODE)
            if not doc:
                print(f"[MISS] {Path(fpath).name} -> NOT in Paperless (import via consume first)")
                misses += 1
                continue

            if method == "checksum":
                match_checksum += 1
            elif method == "filename":
                match_filename += 1

            paperless_checksum = (doc.get("checksum") or "")
            if not paperless_checksum:
                try:
                    detail = http_get(f"/api/documents/{int(doc['id'])}/")
                    paperless_checksum = (detail.get("checksum") or "")
                except Exception:
                    pass
            paperless_checksum = paperless_checksum.lower()
            matched_by = f"match={method}"

            found += 1
            cur_ids = set(doc.get("tags", []))
            need, desired_ids, cur_names, desired_names = compute_final_tag_ids(
                cur_ids, id_to_name, name_to_id, target_name
            )

            if need:
                changed += 1
                print(f"[CHG ] id={doc['id']:>5}  {Path(fpath).name}  -> {target_name}  ({matched_by})")
                if args.verbose:
                    print(f"      our_sha  : {checksum.lower()}")
                    print(f"      pl_sha   : {paperless_checksum}")
                    print(f"      current  : {sorted(cur_names)}")
                    print(f"      final    : {sorted(desired_names)}")
                _set_doc_tags(int(doc["id"]), desired_ids, args.apply)
            else:
                print(f"[OK  ] id={doc['id']:>5}  {Path(fpath).name} (tags OK, {matched_by})")
                if args.verbose:
                    print(f"      our_sha  : {checksum.lower()}")
                    print(f"      pl_sha   : {paperless_checksum}")

    print("\n--- SUMMARY ---")
    print(f"Files scanned      : {total}")
    print(f"Found in Paperless : {found}")
    print(f"{'Applied' if args.apply else 'Would change'}".ljust(18), f": {changed}")
    print(f"Not in Paperless   : {misses}")
    print(f"Matched by checksum: {match_checksum}")
    print(f"Matched by filename: {match_filename}")
    if not args.apply:
        print("\nNo changes applied. Run again with --apply to write changes.")
