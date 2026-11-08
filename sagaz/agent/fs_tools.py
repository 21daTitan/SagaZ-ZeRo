"""Ferramentas de arquivo confinadas à raiz do projeto.

Leitura é livre (escopo ``fs.read``). Escrita/edição exigem ``fs.write`` +
confirmação, e sempre gravam backup antes de alterar.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

from sagaz.agent.core import AgentPolicy, PathEscape, resolve_in_root

_MAX_READ = 400_000
_MAX_FILES = 5_000


class FsTools:
    def __init__(self, root, policy: AgentPolicy):
        self.root = Path(root).resolve()
        self.policy = policy

    # ---- leitura -------------------------------------------------------
    def list(self, path: str = '.') -> dict:
        self.policy.require('fs.read')
        target = resolve_in_root(self.root, path)
        if not target.is_dir():
            raise PathEscape(f'não é um diretório: {path}')
        entries = []
        for item in sorted(target.iterdir()):
            entries.append({'name': item.name,
                            'type': 'dir' if item.is_dir() else ('link' if item.is_symlink() else 'file'),
                            'size': item.stat().st_size if item.is_file() and not item.is_symlink() else None})
        return {'path': str(target.relative_to(self.root)) or '.', 'entries': entries}

    def read(self, path: str, max_bytes: int = _MAX_READ) -> dict:
        self.policy.require('fs.read')
        target = resolve_in_root(self.root, path)
        if target.is_symlink() or not target.is_file():
            raise PathEscape(f'arquivo inexistente ou link: {path}')
        data = target.read_bytes()[: int(max_bytes)]
        try:
            text = data.decode('utf-8')
            binary = False
        except UnicodeDecodeError:
            text = ''
            binary = True
        return {'path': path, 'binary': binary, 'bytes': target.stat().st_size,
                'truncated': target.stat().st_size > len(data), 'content': text}

    def search(self, pattern: str, glob: str = '**/*', max_results: int = 200) -> dict:
        self.policy.require('fs.read')
        try:
            needle = re.compile(pattern)
        except re.error as exc:
            raise PathEscape(f'regex inválida: {exc}')
        hits, scanned = [], 0
        for item in self.root.glob(glob):
            if scanned >= _MAX_FILES or len(hits) >= max_results:
                break
            if item.is_symlink() or not item.is_file():
                continue
            scanned += 1
            try:
                for n, line in enumerate(item.read_text(encoding='utf-8').splitlines(), 1):
                    if needle.search(line):
                        hits.append({'file': str(item.relative_to(self.root)), 'line': n, 'text': line[:300]})
                        if len(hits) >= max_results:
                            break
            except (UnicodeDecodeError, OSError):
                continue
        return {'pattern': pattern, 'count': len(hits), 'matches': hits}

    def stat(self, path: str) -> dict:
        self.policy.require('fs.read')
        target = resolve_in_root(self.root, path)
        info = target.stat()
        return {'path': path, 'exists': True, 'is_dir': target.is_dir(),
                'is_symlink': target.is_symlink(), 'size': info.st_size}

    # ---- escrita (fs.write + confirmação + backup) ---------------------
    def _backup(self, target: Path) -> str | None:
        if not target.exists():
            return None
        stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%f')
        backup_dir = self.root / 'state' / 'backups'
        backup_dir.mkdir(parents=True, exist_ok=True)
        rel = str(target.relative_to(self.root)).replace('/', '__')
        dest = backup_dir / f'{rel}.{stamp}.bak'
        dest.write_bytes(target.read_bytes())
        return str(dest.relative_to(self.root))

    def write(self, path: str, content: str) -> dict:
        self.policy.require('fs.write')
        if not isinstance(content, str):
            raise PathEscape('conteúdo deve ser texto')
        target = resolve_in_root(self.root, path)
        if target.is_symlink():
            raise PathEscape(f'recusando escrever através de symlink: {path}')
        self.policy.confirm(f'gravar arquivo {path} ({len(content)} bytes)')
        backup = self._backup(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding='utf-8')
        return {'path': path, 'written': len(content), 'backup': backup}

    def edit(self, path: str, old: str, new: str) -> dict:
        self.policy.require('fs.write')
        target = resolve_in_root(self.root, path)
        if target.is_symlink() or not target.is_file():
            raise PathEscape(f'arquivo inexistente ou link: {path}')
        text = target.read_text(encoding='utf-8')
        occurrences = text.count(old)
        if occurrences == 0:
            raise PathEscape('trecho a substituir não encontrado')
        if occurrences > 1:
            raise PathEscape(f'trecho ambíguo ({occurrences} ocorrências); torne-o único')
        self.policy.confirm(f'editar {path}')
        backup = self._backup(target)
        target.write_text(text.replace(old, new, 1), encoding='utf-8')
        return {'path': path, 'replaced': 1, 'backup': backup}


__all__ = ['FsTools']
