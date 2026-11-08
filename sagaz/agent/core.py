"""SagaZ coding-agent — núcleo de segurança.

Define os escopos de permissão, o confinamento de caminho (tudo dentro da raiz do
projeto) e a política que decide o que pode rodar e o que exige confirmação.

Nada aqui fala com a rede: é só a camada de controle local.
"""
from __future__ import annotations

from pathlib import Path

# Escopos de permissão do agente. Leitura é separada de escrita/execução/git.
SCOPES = frozenset({'fs.read', 'fs.write', 'exec', 'git.read', 'git.write'})
# Padrão seguro: só leitura. Escrita/execução/push exigem liberação explícita.
READ_ONLY = frozenset({'fs.read', 'git.read'})


class AgentError(Exception):
    """Erro genérico do agente."""


class ScopeDenied(AgentError):
    """Uma ferramenta pediu um escopo que não foi autorizado."""


class ConfirmationRequired(AgentError):
    """Uma ação sensível não foi confirmada pelo operador."""


class PathEscape(AgentError):
    """Tentativa de acessar um caminho fora da raiz do projeto."""


def resolve_in_root(root, relative: str) -> Path:
    """Resolve ``relative`` DENTRO de ``root``; recusa escapes e symlinks que saem.

    - caminho vazio, absoluto que escapa, ``..`` ou symlink que aponta pra fora
      → ``PathEscape``.
    - symlinks que permanecem dentro da raiz são aceitos.
    """
    base = Path(root).resolve()
    if not isinstance(relative, str) or relative.strip() == '':
        raise PathEscape('caminho vazio')
    candidate = base / relative
    try:
        resolved = candidate.resolve()
    except (OSError, RuntimeError):
        raise PathEscape(f'caminho inválido: {relative}')
    if resolved != base and base not in resolved.parents:
        raise PathEscape(f'fora da raiz do projeto: {relative}')
    return resolved


class AgentPolicy:
    """Decide escopo (pode?) e confirmação (o operador autoriza esta ação?).

    ``confirm`` é um callable ``(descricao: str) -> bool``. Em modo não interativo
    sem ``confirm`` e sem ``auto_confirm``, qualquer ação sensível é recusada —
    seguro por padrão.
    """

    def __init__(self, allowed=READ_ONLY, confirm=None, auto_confirm: bool = False):
        invalid = set(allowed) - SCOPES
        if invalid:
            raise AgentError(f'escopos inválidos: {sorted(invalid)}')
        self.allowed = frozenset(allowed)
        self._confirm = confirm
        self.auto_confirm = bool(auto_confirm)

    def grant(self, *scopes) -> 'AgentPolicy':
        """Retorna uma nova política com escopos adicionais liberados."""
        return AgentPolicy(self.allowed | set(scopes), self._confirm, self.auto_confirm)

    def require(self, scope: str) -> None:
        if scope not in SCOPES:
            raise AgentError(f'escopo desconhecido: {scope}')
        if scope not in self.allowed:
            raise ScopeDenied(f'escopo não autorizado: {scope}')

    def confirm(self, action: str) -> None:
        if self.auto_confirm:
            return
        ok = bool(self._confirm(action)) if self._confirm else False
        if not ok:
            raise ConfirmationRequired(action)


__all__ = [
    'SCOPES', 'READ_ONLY', 'AgentError', 'ScopeDenied', 'ConfirmationRequired',
    'PathEscape', 'resolve_in_root', 'AgentPolicy',
]
