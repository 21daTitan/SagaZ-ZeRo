"""Read-only local CTI catalog and search."""
from collections import Counter
import json
from pathlib import Path
import sys

REPO_DATA_FILE = Path(__file__).resolve().parents[2] / "knowledge" / "cti" / "lote2.json"
INSTALLED_DATA_FILE = Path(sys.prefix) / "knowledge" / "cti" / "lote2.json"
DATA_FILE = REPO_DATA_FILE if REPO_DATA_FILE.is_file() else INSTALLED_DATA_FILE
DEFAULT_LIMIT = 20
MAX_LIMIT = 50
MAX_QUERY_LENGTH = 200


class CTIError(RuntimeError):
    """The local CTI catalog is unavailable or malformed."""


def _records(path=None):
    source = Path(path) if path is not None else DATA_FILE
    try:
        data = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CTIError("Local CTI catalog unavailable") from exc
    rows = data.get("records") if isinstance(data, dict) else None
    if not isinstance(rows, list) or not rows or len(rows) > 50:
        raise CTIError("Local CTI catalog has an invalid record list")
    seen = set()
    for row in rows:
        if not isinstance(row, dict) or not all(
            isinstance(row.get(key), str) and row[key].strip()
            for key in ("id", "title", "status")
        ):
            raise CTIError("Local CTI catalog has an invalid record")
        if row["id"] in seen:
            raise CTIError("Local CTI catalog has duplicate IDs")
        for field in ("names", "themes", "keywords", "mitre", "source_refs"):
            if not isinstance(row.get(field, []), list):
                raise CTIError("Local CTI catalog has an invalid " + field + " list")
        if any(not isinstance(value, str) for field in ("names", "themes", "keywords")
               for value in row.get(field, [])):
            raise CTIError("Local CTI catalog has invalid searchable values")
        if any(not isinstance(entity, dict) for entity in row.get("mitre", [])):
            raise CTIError("Local CTI catalog has invalid MITRE entities")
        seen.add(row["id"])
    return rows


def _validate_query(query):
    if not isinstance(query, str):
        raise ValueError("q must be a string")
    query = query.strip()
    if not query or len(query) > MAX_QUERY_LENGTH or any(ord(char) < 32 or ord(char) == 127 for char in query):
        raise ValueError("q must contain 1 to 200 printable characters")
    return query


def _validate_limit(limit):
    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= MAX_LIMIT:
        raise ValueError("limit must be an integer from 1 to 50")
    return limit


def summary(path=None):
    """Return counts and record labels without asserting that records are verified."""
    rows = _records(path)
    statuses = Counter(row["status"] for row in rows)
    themes = Counter(theme for row in rows for theme in row["themes"] if isinstance(theme, str))
    return {
        "count": len(rows),
        "status_counts": dict(sorted(statuses.items())),
        "theme_counts": dict(sorted(themes.items())),
        "records": [{"id": row["id"], "title": row["title"], "status": row["status"]} for row in rows],
    }


def search(query, limit=DEFAULT_LIMIT, path=None):
    """Search IDs, names, themes, keywords and MITRE entity labels locally."""
    query = _validate_query(query)
    limit = _validate_limit(limit)
    needle = query.casefold()
    matches = []
    for row in _records(path):
        searchable = [row["id"], row["title"]]
        searchable.extend(row.get("names", []))
        searchable.extend(row.get("themes", []))
        searchable.extend(row.get("keywords", []))
        searchable.extend(
            value
            for entity in row.get("mitre", [])
            if isinstance(entity, dict)
            for value in (entity.get("id", ""), entity.get("name", ""))
        )
        if any(needle in value.casefold() for value in searchable if isinstance(value, str)):
            matches.append(row)
    return {"query": query, "count": len(matches[:limit]), "results": matches[:limit]}
