import os
from pathlib import Path

def load_dotenv(dotenv_path: str = ".env"):
    p = Path(dotenv_path)
    if not p.exists():
        return
    for line in p.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, v = s.split("=", 1)
        k, v = k.strip(), v.strip()
        if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
            v = v[1:-1]
        os.environ.setdefault(k, v)

load_dotenv()

BASE_URL   = os.getenv("PAPERLESS_BASE_URL", "http://paperless:8000").rstrip("/")
API_TOKEN  = os.getenv("PAPERLESS_API_TOKEN", "")

PLATNE_DIR   = os.getenv("PLATNE_DIR") or ""
NEPLATNE_DIR = os.getenv("NEPLATNE_DIR") or ""
ZRUSENE_DIR  = os.getenv("ZRUSENE_DIR") or ""  # optional

TAG_VALID     = os.getenv("TAG_VALID", "PLATNE")
TAG_EXPIRED   = os.getenv("TAG_EXPIRED", "NEPLATNE")
TAG_DELETED   = os.getenv("TAG_DELETED", "SMAZANE")
TAG_CANCELLED = os.getenv("TAG_CANCELLED", "ZRUSENE")
TAG_PENDING   = os.getenv("TAG_PENDING", "PENDING")

SEARCH_MODE = os.getenv("SEARCH_MODE", "checksum_then_filename").lower()
