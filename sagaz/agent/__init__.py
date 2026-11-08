"""SagaZ-ZeRo coding-agent subsystem (local-only, scope-gated).

Peças: core (escopos/confinamento/política), fs_tools, exec_tools, git_tools,
registry (ferramentas + specs OpenAI), plugins (manifestos), loop (tool-calling
pelo Gateway) e console (CLI). Nada aqui é exposto na rede; o agente roda só no
console local do operador.
"""
from sagaz.agent.core import (
    SCOPES,
    READ_ONLY,
    AgentError,
    AgentPolicy,
    ConfirmationRequired,
    PathEscape,
    ScopeDenied,
    resolve_in_root,
)
from sagaz.agent.registry import Registry, ToolSpec, register_builtin

__all__ = [
    'SCOPES', 'READ_ONLY', 'AgentError', 'AgentPolicy', 'ConfirmationRequired',
    'PathEscape', 'ScopeDenied', 'resolve_in_root',
    'Registry', 'ToolSpec', 'register_builtin',
]
