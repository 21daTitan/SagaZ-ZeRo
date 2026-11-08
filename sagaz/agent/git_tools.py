"""Integração GitHub/Git local para o agente.

Leitura (``git.read``): status, branch atual, diff. Escrita (``git.write``):
branch, add, commit, pull e push. Regras fixas de segurança:
- **nunca** force-push (``--force``/``-f``/``--force-with-lease``/refspec ``+``);
- push **sempre** confirma;
- usa as credenciais locais do ``git`` do usuário; nenhum token é lido ou gravado aqui.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

from sagaz.agent.core import AgentError, AgentPolicy

_FORCE_FLAGS = {'--force', '-f', '--force-with-lease'}


def _reject_force(args) -> None:
    for a in args:
        if a in _FORCE_FLAGS or (isinstance(a, str) and a.startswith('+')):
            raise AgentError('force-push é proibido nesta edição')


class GitTools:
    def __init__(self, root, policy: AgentPolicy):
        self.root = Path(root).resolve()
        self.policy = policy

    def _git(self, *args, timeout: int = 60) -> dict:
        proc = subprocess.run(['git', '-C', str(self.root), *args],
                              capture_output=True, text=True, timeout=timeout)
        return {'args': list(args), 'returncode': proc.returncode,
                'stdout': (proc.stdout or '')[:20_000], 'stderr': (proc.stderr or '')[:8_000]}

    # ---- leitura -------------------------------------------------------
    def status(self) -> dict:
        self.policy.require('git.read')
        return self._git('status', '--porcelain=v1', '--branch')

    def current_branch(self) -> dict:
        self.policy.require('git.read')
        return self._git('rev-parse', '--abbrev-ref', 'HEAD')

    def diff(self, staged: bool = False) -> dict:
        self.policy.require('git.read')
        return self._git('diff', '--cached') if staged else self._git('diff')

    # ---- escrita -------------------------------------------------------
    def branch(self, name: str) -> dict:
        self.policy.require('git.write')
        if not isinstance(name, str) or not name.strip() or name.startswith('-'):
            raise AgentError('nome de branch inválido')
        return self._git('switch', '-c', name)

    def add(self, paths=None) -> dict:
        self.policy.require('git.write')
        targets = list(paths) if paths else ['-A']
        for t in targets:
            if isinstance(t, str) and t.startswith('-') and t != '-A':
                raise AgentError(f'caminho inválido: {t}')
        return self._git('add', *targets)

    def commit(self, message: str) -> dict:
        self.policy.require('git.write')
        if not isinstance(message, str) or not message.strip():
            raise AgentError('mensagem de commit vazia')
        return self._git('commit', '-m', message)

    def pull(self, remote: str = 'origin', branch: str | None = None) -> dict:
        self.policy.require('git.write')
        args = ['pull', remote] + ([branch] if branch else [])
        _reject_force(args)
        return self._git(*args)

    def push(self, remote: str = 'origin', branch: str | None = None, set_upstream: bool = True) -> dict:
        self.policy.require('git.write')
        if branch is None:
            branch = (self._git('rev-parse', '--abbrev-ref', 'HEAD')['stdout'] or '').strip()
        args = ['push'] + (['-u'] if set_upstream else []) + [remote, branch]
        _reject_force(args)
        self.policy.confirm(f'git push {remote} {branch}')
        return self._git(*args)


__all__ = ['GitTools']
