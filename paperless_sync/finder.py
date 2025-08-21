import unicodedata, urllib.parse, urllib.error
from pathlib import Path
from typing import Optional, Dict
from .http import http_get

# lokální index checksum -> dokument
_DOC_BY_CHECKSUM: Dict[str, dict] = {}
_ALL_INDEXED = False

def _norm(s: str) -> str:
    return unicodedata.normalize("NFKC", s or "").casefold()

def _index_all_documents():
    global _ALL_INDEXED
    if _ALL_INDEXED:
        return
    page = 1
    while True:
        res = http_get(f"/api/documents/?page={page}&page_size=100")
        for d in res.get("results", []):
            csum = (d.get("checksum") or "").lower()
            if csum:
                _DOC_BY_CHECKSUM.setdefault(csum, d)
        if not res.get("next"):
            break
        page += 1
    _ALL_INDEXED = True

def find_doc_by_checksum(checksum: str) -> Optional[dict]:
    target = (checksum or "").lower()
    if not target:
        return None
    # cache
    if target in _DOC_BY_CHECKSUM:
        return _DOC_BY_CHECKSUM[target]
    # přímý filtr (pokud API umí)
    try:
        res = http_get(f"/api/documents/?page_size=5&checksum={urllib.parse.quote(target)}")
        for d in res.get("results", []):
            if (d.get("checksum") or "").lower() == target:
                _DOC_BY_CHECKSUM[target] = d
                return d
    except urllib.error.HTTPError:
        pass
    # fallback: lokální index
    _index_all_documents()
    return _DOC_BY_CHECKSUM.get(target, None)

def find_doc_by_filename_strict(filename: str) -> Optional[dict]:
    name = Path(filename).name
    stem = Path(filename).stem
    q = urllib.parse.quote(name)
    res = http_get(f"/api/documents/?page_size=50&query={q}")
    cand = res.get("results", [])
    # 1) exact original_filename
    for d in cand:
        orig = d.get("original_filename") or ""
        if _norm(orig) == _norm(name):
            return d
    # 2) exact title == stem
    for d in cand:
        title = d.get("title") or ""
        if _norm(title) == _norm(stem):
            return d
    # 3) fallback: query podle stem
    q2 = urllib.parse.quote(stem)
    res2 = http_get(f"/api/documents/?page_size=50&query={q2}")
    cand2 = res2.get("results", [])
    for d in cand2:
        orig = d.get("original_filename") or ""
        title = d.get("title") or ""
        if _norm(orig) == _norm(name) or _norm(title) == _norm(stem):
            return d
    return None

def find_doc_resilient(file_path: str, checksum: str, search_mode: str) -> Optional[dict]:
    m = (search_mode or "checksum_then_filename").lower()
    if m == "checksum":
        d = find_doc_by_checksum(checksum)
        return d, ("checksum" if d else None)
    if m == "filename":
        d = find_doc_by_filename_strict(file_path)
        return d, ("filename" if d else None)
    d = find_doc_by_checksum(checksum)
    if d:
        return d, "checksum"
    d = find_doc_by_filename_strict(file_path)
    return d, ("filename" if d else None)
