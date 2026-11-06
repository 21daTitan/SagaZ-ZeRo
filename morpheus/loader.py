"""Metadata-only local prompt manifest loader. No remote execution or corpus bundling."""
import hashlib
import json
from pathlib import Path


def manifest(path):
    path = Path(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("entries"), list):
        raise ValueError("Invalid manifest")
    for entry in data["entries"]:
        if not isinstance(entry, dict) or not all(isinstance(entry.get(k), str) for k in ("id", "path", "sha256")):
            raise ValueError("Invalid manifest entry")
        if len(entry["sha256"]) != 64 or any(c not in "0123456789abcdef" for c in entry["sha256"]):
            raise ValueError("Invalid SHA256")
    return data


def verify_files(path, root):
    entries = manifest(path)["entries"]
    base = Path(root).resolve()
    status = []
    for entry in entries:
        relative = Path(entry["path"])
        if relative.is_absolute() or '..' in relative.parts:
            status.append({"id": entry["id"], "valid": False})
            continue
        target = (base / relative).resolve()
        valid = target.is_file() and target.is_relative_to(base) and hashlib.sha256(target.read_bytes()).hexdigest() == entry["sha256"]
        status.append({"id": entry["id"], "valid": valid})
    return status
