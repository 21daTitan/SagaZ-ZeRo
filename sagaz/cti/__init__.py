"""Read-only CTI knowledge for SagaZ ZeRo; unverified claims are not authoritative."""
from __future__ import annotations
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATASET = ROOT / 'knowledge' / 'cti' / 'lote2.json'
ID_PATTERN = re.compile(r'^ALFA-CTI-\d{4}$')
DEPRECATED_MITRE = {'T1138': 'T1546.011', 'T1116': 'T1553.002'}


def _fold(text: str) -> str:
    return ''.join(c for c in unicodedata.normalize('NFKD', text.casefold()) if not unicodedata.combining(c))


def records(path: Path | None = None) -> list[dict]:
    target = Path(path) if path is not None else DATASET
    raw = json.loads(target.read_text(encoding='utf-8'))
    if not isinstance(raw, list):
        raise ValueError('CTI dataset must be a JSON array')
    ids = set()
    result = []
    for row in raw:
        if not isinstance(row, dict) or not ID_PATTERN.fullmatch(str(row.get('knowledge_id', ''))):
            raise ValueError('Invalid CTI record ID')
        if row['knowledge_id'] in ids:
            raise ValueError('Duplicate CTI record ID')
        ids.add(row['knowledge_id'])
        if not isinstance(row.get('topic'), str) or not row['topic'].strip():
            raise ValueError('Missing topic')
        if not isinstance(row.get('technical_description'), str):
            raise ValueError('Missing description')
        if not isinstance(row.get('sources'), list) or not all(isinstance(u, str) and u.startswith('https://') for u in row['sources']):
            raise ValueError('Invalid sources')
        normalized = dict(row)
        # Ingestion cannot promote an externally asserted verification result.
        normalized['evidence_status'] = 'unverified'
        normalized['confidence'] = 'unassessed'
        normalized['mitre_techniques'] = [DEPRECATED_MITRE.get(mid, mid) for mid in row.get('mitre_techniques', [])]
        result.append(normalized)
    return result


def search(query: str, limit: int = 10) -> dict:
    if not isinstance(query, str) or not 1 <= len(query.strip()) <= 120:
        raise ValueError('Query must contain 1–120 characters')
    if type(limit) is not int or not 1 <= limit <= 20:
        raise ValueError('Limit must be an integer between 1 and 20')
    needle = _fold(query.strip())
    found = []
    for row in records():
        haystack = _fold(' '.join([row['topic'], row['technical_description'], ' '.join(row.get('related_entities', [])), row.get('category', '')]))
        if needle in haystack:
            found.append(row)
    return {'query': query, 'count': len(found), 'entries': found[:limit], 'evidence_notice': 'Dados fornecidos pelo operador, ainda não verificados em fontes primárias.'}


def summary() -> dict:
    data = records()
    return {'collection': 'ALFA-CTI / SagaZ ZeRo', 'records': len(data), 'verified': 0,
            'unverified': len(data), 'ids': [row['knowledge_id'] for row in data],
            'mode': 'read_only', 'sources_checked': False}
