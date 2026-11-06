"""Public capability metadata. Credentials never leave the process."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def skills():
    entries = []
    for folder in sorted((ROOT / '.agents/skills').iterdir()):
        file = folder / 'SKILL.md'
        if not file.is_file() or folder.is_symlink():
            continue
        lines = file.read_text(encoding='utf-8').splitlines()
        description = ''
        for index, line in enumerate(lines):
            if line.startswith('description:'):
                description = line.partition(':')[2].strip()
                if description in ('>', '|', '>-', '|-'):
                    parts = []
                    for following in lines[index+1:]:
                        if following and not following.startswith((' ', '\t')):
                            break
                        parts.append(following.strip())
                    description = ' '.join(parts).strip()
                break
        entries.append({'id': folder.name, 'description': description, 'available': True})
    return {'entries': entries, 'count': len(entries)}


def connection():
    return {
        'configured': bool(os.environ.get('DSANT_BASE_URL') and os.environ.get('DSANT_MODEL')),
        'model': os.environ.get('DSANT_MODEL', ''),
        'key_present': bool(os.environ.get('DSANT_API_KEY')),
        'verified': False,
        'protocol': 'OpenAI-compatible chat completions',
        'presets': [
            {'id': 'ollama', 'label': 'Ollama local', 'base_url': 'http://127.0.0.1:11434/v1'},
            {'id': 'router', 'label': '9Router / endpoint próprio', 'base_url': 'DSANT_BASE_URL'},
        ],
    }
