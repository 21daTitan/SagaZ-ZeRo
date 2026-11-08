"""Registro de ferramentas do agente.

Cada ferramenta tem nome, descrição, escopo exigido, schema de parâmetros
(estilo JSON Schema / OpenAI function calling) e um handler. O registro só
oferece ao modelo as ferramentas cujo escopo está liberado na política, e toda
chamada passa por ``policy.require(scope)`` antes de executar.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from sagaz.agent.core import AgentError, AgentPolicy
from sagaz.agent.exec_tools import ExecTools
from sagaz.agent.fs_tools import FsTools
from sagaz.agent.git_tools import GitTools


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    scope: str
    parameters: dict
    handler: Callable[..., dict]


class Registry:
    def __init__(self, policy: AgentPolicy):
        self.policy = policy
        self._tools: dict[str, ToolSpec] = {}

    def register(self, spec: ToolSpec) -> None:
        from sagaz.agent.core import SCOPES
        if spec.scope not in SCOPES:
            raise AgentError(f'escopo inválido na ferramenta {spec.name}: {spec.scope}')
        if spec.name in self._tools:
            raise AgentError(f'ferramenta duplicada: {spec.name}')
        self._tools[spec.name] = spec

    def names(self) -> list[str]:
        return sorted(self._tools)

    def enabled(self) -> list[ToolSpec]:
        """Só as ferramentas cujo escopo está autorizado na política."""
        return [s for s in self._tools.values() if s.scope in self.policy.allowed]

    def openai_tools(self) -> list[dict]:
        return [{'type': 'function',
                 'function': {'name': s.name, 'description': s.description, 'parameters': s.parameters}}
                for s in self.enabled()]

    def call(self, name: str, arguments: dict) -> dict:
        spec = self._tools.get(name)
        if spec is None:
            raise AgentError(f'ferramenta desconhecida: {name}')
        self.policy.require(spec.scope)  # escopo verificado de novo na execução
        if not isinstance(arguments, dict):
            raise AgentError('argumentos devem ser um objeto')
        return spec.handler(**arguments)


def _s(props: dict, required: list[str]) -> dict:
    return {'type': 'object', 'properties': props, 'required': required, 'additionalProperties': False}


def register_builtin(registry: Registry, root, exec_tool=None) -> Registry:
    """Registra o conjunto padrão de ferramentas de arquivo, exec e git.

    ``exec_tool`` permite trocar o executor (ex.: ``SandboxExec`` em container);
    quando ausente, usa o ``ExecTools`` local padrão.
    """
    root = Path(root).resolve()
    fs = FsTools(root, registry.policy)
    ex = exec_tool if exec_tool is not None else ExecTools(root, registry.policy)
    git = GitTools(root, registry.policy)

    specs = [
        ToolSpec('fs_list', 'Lista um diretório do projeto.', 'fs.read',
                 _s({'path': {'type': 'string'}}, []), lambda path='.': fs.list(path)),
        ToolSpec('fs_read', 'Lê um arquivo de texto do projeto.', 'fs.read',
                 _s({'path': {'type': 'string'}}, ['path']), lambda path: fs.read(path)),
        ToolSpec('fs_search', 'Busca por regex nos arquivos do projeto.', 'fs.read',
                 _s({'pattern': {'type': 'string'}, 'glob': {'type': 'string'}}, ['pattern']),
                 lambda pattern, glob='**/*': fs.search(pattern, glob)),
        ToolSpec('fs_stat', 'Metadados de um caminho.', 'fs.read',
                 _s({'path': {'type': 'string'}}, ['path']), lambda path: fs.stat(path)),
        ToolSpec('fs_write', 'Grava um arquivo (com backup; exige confirmação).', 'fs.write',
                 _s({'path': {'type': 'string'}, 'content': {'type': 'string'}}, ['path', 'content']),
                 lambda path, content: fs.write(path, content)),
        ToolSpec('fs_edit', 'Substitui um trecho único em um arquivo (backup; confirma).', 'fs.write',
                 _s({'path': {'type': 'string'}, 'old': {'type': 'string'}, 'new': {'type': 'string'}},
                    ['path', 'old', 'new']), lambda path, old, new: fs.edit(path, old, new)),
        ToolSpec('run_command',
                 ('Executa um comando de shell em sandbox (container)' if exec_tool is not None
                  else 'Executa um comando de shell na raiz') + ' — trava destrutiva + confirmação.',
                 'exec', _s({'command': {'type': 'string'}}, ['command']), lambda command: ex.run(command)),
        ToolSpec('git_status', 'git status do projeto.', 'git.read',
                 _s({}, []), lambda: git.status()),
        ToolSpec('git_diff', 'git diff (ou --cached).', 'git.read',
                 _s({'staged': {'type': 'boolean'}}, []), lambda staged=False: git.diff(staged)),
        ToolSpec('git_branch', 'Cria e troca para uma branch.', 'git.write',
                 _s({'name': {'type': 'string'}}, ['name']), lambda name: git.branch(name)),
        ToolSpec('git_add', 'git add dos caminhos (padrão: tudo).', 'git.write',
                 _s({'paths': {'type': 'array', 'items': {'type': 'string'}}}, []),
                 lambda paths=None: git.add(paths)),
        ToolSpec('git_commit', 'git commit -m.', 'git.write',
                 _s({'message': {'type': 'string'}}, ['message']), lambda message: git.commit(message)),
        ToolSpec('git_push', 'git push (sem force; confirma).', 'git.write',
                 _s({'remote': {'type': 'string'}, 'branch': {'type': 'string'}}, []),
                 lambda remote='origin', branch=None: git.push(remote, branch)),
    ]
    for spec in specs:
        registry.register(spec)
    return registry


__all__ = ['ToolSpec', 'Registry', 'register_builtin']
