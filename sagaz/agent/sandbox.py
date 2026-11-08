"""Execução de comandos em sandbox de container (Fase 6).

Alternativa mais segura ao `run_command`: roda o comando dentro de um container
Docker, com a raiz do projeto montada em `/work`, **sem rede por padrão**, com
limites de memória/CPU/processos e mantendo a propriedade dos arquivos do host.

Mantém a mesma trava de segurança do executor normal: exige o escopo `exec` e
confirma comandos destrutivos. Se o Docker não estiver disponível, retorna um
resultado de erro explícito (nunca cai para execução sem isolamento).
"""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

from sagaz.agent.core import AgentPolicy
from sagaz.god import is_destructive_command

_IMAGE = os.environ.get('SAGAZ_SANDBOX_IMAGE', 'python:3.12-slim')
_OUT_LIMIT = 20_000


def available() -> bool:
    return shutil.which('docker') is not None


class SandboxExec:
    def __init__(self, root, policy: AgentPolicy, timeout: int = 60,
                 image: str = _IMAGE, allow_network: bool = False):
        self.root = Path(root).resolve()
        self.policy = policy
        self.timeout = int(timeout)
        self.image = image
        self.allow_network = bool(allow_network)

    def build_command(self, command: str, timeout: int) -> list[str]:
        """Monta o `docker run` isolado (função pura, testável)."""
        args = [
            'docker', 'run', '--rm', '--interactive=false',
            '--network', 'bridge' if self.allow_network else 'none',
            '--memory', '512m', '--cpus', '1', '--pids-limit', '256',
            '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges',
            '--user', f'{os.getuid()}:{os.getgid()}',
            '--volume', f'{self.root}:/work', '--workdir', '/work',
            self.image, 'timeout', str(int(timeout)), 'sh', '-c', command,
        ]
        return args

    def run(self, command: str, timeout: int | None = None) -> dict:
        self.policy.require('exec')
        if not isinstance(command, str) or not command.strip():
            raise ValueError('comando vazio')
        destructive = is_destructive_command(command)
        if destructive:
            self.policy.confirm(f'executar em sandbox (comando destrutivo): {command}')
        if not available():
            return {'command': command, 'sandbox': True, 'available': False, 'returncode': None,
                    'stdout': '', 'stderr': 'Docker indisponível; comando não executado.',
                    'destructive': destructive, 'timed_out': False}
        limit = int(timeout or self.timeout)
        argv = self.build_command(command, limit)
        try:
            proc = subprocess.run(argv, capture_output=True, text=True, timeout=limit + 10)
        except subprocess.TimeoutExpired:
            return {'command': command, 'sandbox': True, 'available': True, 'timed_out': True,
                    'returncode': None, 'stdout': '', 'stderr': f'tempo excedido ({limit}s)',
                    'destructive': destructive}
        return {'command': command, 'sandbox': True, 'available': True, 'timed_out': False,
                'returncode': proc.returncode, 'stdout': (proc.stdout or '')[:_OUT_LIMIT],
                'stderr': (proc.stderr or '')[:_OUT_LIMIT], 'destructive': destructive,
                'network': self.allow_network}


__all__ = ['SandboxExec', 'available']
