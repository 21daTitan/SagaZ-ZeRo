"""Report branding replacements while preserving original author attribution."""
import re
from pathlib import Path

PROTECTED = ("Morlsara Code Nexus", "Mörlsara", "DarkyHArry", "Code Nexus", "cassandra-agent")
RULES = (("CASSANDRA_", "SAGA_"), ("Evil Cassandra", "SagaZ ZeRo"))


def transform(text: str) -> tuple[str, list[str]]:
    if not isinstance(text, str):
        raise TypeError("text required")
    changed = []
    lines = []
    for line in text.splitlines(keepends=True):
        if any(key in line for key in PROTECTED):
            lines.append(line)
            continue
        for old, new in RULES:
            if old in line:
                line = line.replace(old, new)
                changed.append(old)
        lines.append(line)
    return "".join(lines), sorted(set(changed))


def scan(path: str | Path) -> dict:
    file = Path(path)
    original = file.read_text(encoding="utf-8")
    final, changed = transform(original)
    return {"path": str(file), "changed": final != original, "rules": changed, "output": final}
