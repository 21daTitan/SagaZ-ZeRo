"""Console do agente de código SagaZ-ZeRo (CLI).

`sagaz agent "<objetivo>" [--allow fs.write,exec,git.write] [--yes]`
  → roda o loop do agente sobre o diretório atual.

`sagaz plugin list|enable|disable [nome]` → gerencia plugins.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from sagaz.agent.core import READ_ONLY, SCOPES, AgentError, AgentPolicy
from sagaz.agent.plugins import PluginManager
from sagaz.agent.registry import Registry, register_builtin

_TTY = sys.stdout.isatty()
_C = '\x1b[38;5;51m' if _TTY else ''
_G = '\x1b[38;5;83m' if _TTY else ''
_R = '\x1b[38;5;203m' if _TTY else ''
_D = '\x1b[38;5;110m' if _TTY else ''
_Z = '\x1b[0m' if _TTY else ''


def _parse_scopes(allow: str) -> set[str]:
    wanted = {s.strip() for chunk in (allow or '').replace(',', ' ').split() for s in [chunk] if s.strip()}
    invalid = wanted - SCOPES
    if invalid:
        raise AgentError(f'escopos inválidos: {sorted(invalid)} (válidos: {sorted(SCOPES)})')
    return wanted


def _confirmer(auto_yes: bool):
    if auto_yes:
        return (lambda action: True)

    def ask(action: str) -> bool:
        try:
            return input(f'  {_R}⚠ confirmar:{_Z} {action} ? [s/N] ').strip().lower() in ('s', 'sim', 'y', 'yes')
        except (EOFError, KeyboardInterrupt):
            return False
    return ask


def build_registry(root, allow='', auto_yes=False):
    policy = AgentPolicy(READ_ONLY | _parse_scopes(allow), confirm=_confirmer(auto_yes), auto_confirm=auto_yes)
    registry = register_builtin(Registry(policy), root)
    try:
        loaded = PluginManager(root).load_into(registry)
    except AgentError as exc:
        print(f'{_R}[plugins] ignorados: {exc}{_Z}', file=sys.stderr)
        loaded = []
    return registry, policy, loaded


def _print_event(event: dict) -> None:
    if event['type'] == 'tool':
        mark = f'{_G}✓{_Z}' if event['ok'] else f'{_R}✗{_Z}'
        print(f'  {mark} {_C}{event["name"]}{_Z} {_D}{event["content"][:300]}{_Z}')
    elif event['type'] == 'final':
        print(f'\n{_G}SagaZ ❯{_Z} {event["answer"]}\n')
    elif event['type'] == 'limit':
        print(f'  {_R}(limite de iterações){_Z}')


def run(goal=None, allow='', auto_yes=False, root=None, max_iterations=None) -> int:
    from sagaz.god import resolve
    from sagaz.provider_config import load as load_provider
    from sagaz.gateway.router import ProviderUnavailable

    root = Path(root or Path.cwd()).resolve()
    try:
        load_provider()
    except Exception:
        pass
    registry, policy, loaded = build_registry(root, allow, auto_yes)
    iters = int(max_iterations or resolve().max_iterations or 8)

    from sagaz.agent.loop import AgentLoop
    loop = AgentLoop(registry, root=root, max_iterations=iters)

    granted = ', '.join(sorted(policy.allowed))
    print(f'{_C}SagaZ-ZeRo · agente de código{_Z}  {_D}raiz: {root.name} · escopos: {granted}'
          f'{" · plugins: " + ",".join(loaded) if loaded else ""}{_Z}')

    def once(objective: str) -> None:
        try:
            loop.run(objective, on_event=_print_event)
        except ProviderUnavailable:
            print(f'  {_R}Sem provedor conectado.{_Z} Rode `python3 -m sagaz operator` e use /conectar.')
        except (AgentError, ValueError) as exc:
            print(f'  {_R}{exc}{_Z}')

    if goal:
        once(goal)
        return 0
    print(f'{_D}Digite o objetivo (ou "sair"). Ferramentas de escrita/exec/git exigem --allow.{_Z}')
    while True:
        try:
            line = input(f'{_C}objetivo ❯ {_Z}').strip()
        except (EOFError, KeyboardInterrupt):
            print('\n  até mais.')
            return 0
        if line.lower() in ('sair', 'exit', 'quit'):
            return 0
        if line:
            once(line)


def plugin_cli(operation: str, name=None, root=None) -> int:
    manager = PluginManager(Path(root or Path.cwd()).resolve())
    if operation == 'list':
        print(json.dumps(manager.list(), ensure_ascii=False, indent=2))
    elif operation in ('enable', 'disable'):
        if not name:
            print('informe o nome do plugin', file=sys.stderr)
            return 1
        action = manager.enable if operation == 'enable' else manager.disable
        print(json.dumps(action(name), ensure_ascii=False, indent=2))
    return 0


__all__ = ['run', 'plugin_cli', 'build_registry']
