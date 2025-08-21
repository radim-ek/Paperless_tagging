import hashlib
from pathlib import Path
from typing import Iterator

def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def iter_files(root: str) -> Iterator[str]:
    if not root:
        return
    p = Path(root)
    if not p.exists():
        print(f"[WARN] Missing dir: {root}")
        return
    for f in p.rglob("*"):
        if f.is_file():
            yield str(f)
