"""Read-only classification of upstream files; does not fetch or mutate a repo."""
import hashlib
from pathlib import Path

ORIGIN_REPO = "https://github.com/DarkyHArry/cassandra-agent"


def file_hash(file):
    return hashlib.sha256(Path(file).read_bytes()).hexdigest()


def compare_directories(upstream: Path, local: Path):
    upstream, local = Path(upstream).resolve(), Path(local).resolve()
    if not upstream.is_dir() or not local.is_dir():
        raise ValueError("Both directories must exist")
    result = []
    for source in sorted(upstream.rglob("*")):
        if not source.is_file() or source.is_symlink() or any(x in {".git", ".env", "node_modules"} for x in source.relative_to(upstream).parts):
            continue
        relative = source.relative_to(upstream)
        dest = local / relative
        if dest.is_symlink():
            category = "unsafe_symlink"
        elif not dest.exists():
            category = "upstream_only"
        elif not dest.is_file():
            category = "type_conflict"
        elif file_hash(source) == file_hash(dest):
            category = "identical"
        else:
            category = "conflict_review_required"
        result.append({"path": relative.as_posix(), "category": category})
    return result
