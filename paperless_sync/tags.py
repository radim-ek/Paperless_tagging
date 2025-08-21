from typing import Tuple, Set
from .http import http_get, http_post
from .config import TAG_VALID, TAG_EXPIRED, TAG_DELETED, TAG_CANCELLED, TAG_PENDING

def get_all_tags():
    id_to_name, name_to_id = {}, {}
    page = 1
    while True:
        res = http_get(f"/api/tags/?page={page}&page_size=100")
        for t in res.get("results", []):
            tid = int(t["id"])
            name = t.get("name")
            id_to_name[tid] = name
            name_to_id[name] = tid
        if not res.get("next"):
            break
        page += 1
    return id_to_name, name_to_id

def ensure_tag(name: str, name_to_id: dict) -> int:
    if name in name_to_id:
        return name_to_id[name]
    created = http_post("/api/tags/", {"name": name})
    tid = int(created["id"])
    name_to_id[name] = tid
    return tid

STATE_TAGS = [TAG_VALID, TAG_EXPIRED, TAG_DELETED, TAG_CANCELLED]

def compute_final_tag_ids(current_ids: Set[int], id_to_name: dict, name_to_id: dict, target_name: str):
    """
    Vrátí: (need_change: bool, desired_ids: set, current_names: set, desired_names: set)
    - vyluč stavové tagy + PENDING (ponech ostatní tagy)
    """
    current_names = {id_to_name.get(tid, f"#{tid}") for tid in current_ids}
    others = set(STATE_TAGS + [TAG_PENDING])
    desired_names = (current_names | {target_name}) - (others - {target_name})

    desired_ids = set()
    for name in desired_names:
        if name.startswith("#"):
            try:
                desired_ids.add(int(name[1:]))
            except:
                pass
        else:
            desired_ids.add(ensure_tag(name, name_to_id))
    need_change = desired_ids != set(current_ids)
    return need_change, desired_ids, current_names, desired_names
