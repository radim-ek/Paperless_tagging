import json, sys, urllib.request, urllib.error
from .config import BASE_URL, API_TOKEN

def _headers():
    if not API_TOKEN:
        print("ERROR: PAPERLESS_API_TOKEN missing in .env", file=sys.stderr)
        raise SystemExit(2)
    return {
        "Authorization": f"Token {API_TOKEN}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

def http_get(path: str, timeout: int = 45) -> dict:
    req = urllib.request.Request(BASE_URL + path, headers=_headers(), method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))

def http_post(path: str, payload: dict, timeout: int = 45) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(BASE_URL + path, headers=_headers(), data=data, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))

def http_patch(path: str, payload: dict, timeout: int = 45) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(BASE_URL + path, headers=_headers(), data=data, method="PATCH")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))
