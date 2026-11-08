"""Execução de comandos com a trava de segurança do SagaZ.

Exige o escopo ``exec``. Comandos classificados como destrutivos por
``god.is_destructive_command`` exigem confirmação explícita. Sempre com timeout,
rodando na raiz do projeto, sem ``sudo`` automático.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

from sagaz.agent.core import AgentPolicy
from sagaz.god import is_destructive_command

_OUT_LIMIT = 20_000
_DEFAULT_TIMEOUT = 60


class ExecTools:
    def __init__(self, root, policy: AgentPolicy, timeout: int = _DEFAULT_TIMEOUT):
        self.root = Path(root).resolve()
        self.policy = policy
        self.timeout = int(timeout)

    def run(self, command: str, timeout: int | None = None) -> dict:
        self.policy.require('exec')
        if not isinstance(command, str) or not command.strip():
            raise ValueError('comando vazio')
        destructive = is_destructive_command(command)
        if destructive:
            self.policy.confirm(f'executar comando potencialmente destrutivo: {command}')
        limit = int(timeout or self.timeout)
        try:
            proc = subprocess.run(command, shell=True, cwd=str(self.root),
                                   capture_output=True, text=True, timeout=limit)
        except subprocess.TimeoutExpired:
            return {'command': command, 'timed_out': True, 'returncode': None,
                    'stdout': '', 'stderr': f'tempo excedido ({limit}s)', 'destructive': destructive}
        out = proc.stdout or ''
        err = proc.stderr or ''
        return {'command': command, 'timed_out': False, 'returncode': proc.returncode,
                'stdout': out[:_OUT_LIMIT], 'stderr': err[:_OUT_LIMIT],
                'truncated': len(out) > _OUT_LIMIT or len(err) > _OUT_LIMIT,
                'destructive': destructive}


__all__ = ['ExecTools']
