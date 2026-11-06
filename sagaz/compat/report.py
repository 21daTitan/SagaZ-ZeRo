"""Render a proposed upstream compatibility report without modifying files."""
from collections import Counter
from sagaz.compat.upstream import ORIGIN_REPO


def markdown(rows):
    counts = Counter(item["category"] for item in rows)
    lines = ["# Compatibilidade upstream", "", f"Origem: {ORIGIN_REPO}", "",
             "Nenhuma alteração é aplicada automaticamente.", "", "## Categorias", ""]
    lines += [f"- {category}: {count}" for category, count in sorted(counts.items())]
    lines += ["", "## Arquivos", "", "| Arquivo | Status |", "|---|---|"]
    for item in rows:
        lines.append(f"| `{item['path']}` | `{item['category']}` |")
    return "\n".join(lines) + "\n"
