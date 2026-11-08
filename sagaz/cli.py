"""SagaZ CLI: local operation and explicit read-only diagnostics."""
import argparse
import json
import os
import sys
from pathlib import Path

from sagaz.app import cli as interactive_cli, operator_shell, serve
from sagaz.attribution import credits
from sagaz.catalog import connection
from sagaz.gateway.service import Gateway
from sagaz.pix import static_brcode
from sagaz.services import operator_command
from sagaz.discord_memory import DiscordMemory, load_json
from sagaz.god import public_dict, resolve
from sagaz.compat.upstream import compare_directories
from sagaz.compat.report import markdown
from guard.status import status as guard_status

ROOT = Path(__file__).resolve().parents[1]


def main(argv=None):
    try:
        from sagaz.provider_config import load as _load_provider
        _load_provider()
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f'[provedor] configuração salva ignorada: {exc}', file=sys.stderr)
    parser = argparse.ArgumentParser(description='HooLeeSheet · SagaZ ZeRo v3.7.0')
    parser.add_argument('--web', action='store_true', help='Legacy: launch local Web UI')
    parser.add_argument('--port', type=int, default=8080)
    parser.add_argument('--use-model', action='store_true')
    sub = parser.add_subparsers(dest='command')
    create = sub.add_parser('criar', help='Acionar a skill dSant-CreaTor')
    create.add_argument('briefing')
    create.add_argument('--use-model', action='store_true', default=argparse.SUPPRESS)
    sub.add_parser('shell', help='Abrir shell interativo com as permissões da conta atual')
    operator = sub.add_parser('operator', help='Console operador HooLeeSh33t (TUI) com chat BYOK real')
    operator.add_argument('--use-model', action='store_true', default=argparse.SUPPRESS)
    agent = sub.add_parser('agent', help='Agente de código: ferramentas locais + modelo (tool-calling)')
    agent.add_argument('goal', nargs='?', help='objetivo; sem ele, abre modo interativo')
    agent.add_argument('--allow', default='', help='escopos extras: fs.write,exec,git.write')
    agent.add_argument('--yes', action='store_true', help='auto-confirma ações sensíveis (perigoso)')
    plugin = sub.add_parser('plugin', help='Plugins que registram ferramentas no agente')
    plugin.add_argument('operation', choices=('list', 'enable', 'disable'))
    plugin.add_argument('name', nargs='?')
    sub.add_parser('doctor')
    sub.add_parser('credits')
    sub.add_parser('connect')
    sub.add_parser('guard')
    god = sub.add_parser('god', help='Mostrar ou selecionar o perfil de operação')
    god.add_argument('level', nargs='?', choices=('deus', 'devocional'))
    discord = sub.add_parser('discord', help='Memória Discord local e consentida')
    discord.add_argument('operation', choices=('stats', 'search', 'ingest'))
    discord.add_argument('value', nargs='?')
    discord.add_argument('--db', type=Path, default=ROOT/'projects/sagaz/discord_memory.sqlite3')
    discord.add_argument('--consent', action='store_true')
    serve_p = sub.add_parser('serve')
    serve_p.add_argument('--port', type=int, default=8080)
    pix = sub.add_parser('pix')
    pix.add_argument('--amount', type=str, default=None)
    compat = sub.add_parser('compat')
    compat.add_argument('upstream', type=Path)
    compat.add_argument('--local', type=Path, default=ROOT)
    gateway = sub.add_parser('gateway')
    gateway.add_argument('operation', choices=('cost', 'audit-verify', 'audit-checkpoint', 'capability', 'models'))
    args = parser.parse_args(argv)
    if args.web or args.command=='serve':
        serve(args.port)
    elif args.command is None:
        interactive_cli(args.use_model)
    elif args.command == 'criar':
        try:
            print(operator_command('/criar ' + args.briefing, use_model=args.use_model)['answer'])
        except (ValueError, OSError) as exc:
            parser.exit(1, f'Erro: {exc}\n')
    elif args.command == 'shell':
        try:
            return operator_shell()
        except (ValueError, OSError) as exc:
            parser.exit(1, f'Erro: {exc}\n')
    elif args.command == 'operator':
        from sagaz.operator_tui import run as operator_console
        return operator_console(getattr(args, 'use_model', False))
    elif args.command == 'agent':
        from sagaz.agent.console import run as agent_run
        return agent_run(goal=args.goal, allow=args.allow, auto_yes=args.yes)
    elif args.command == 'plugin':
        from sagaz.agent.console import plugin_cli
        return plugin_cli(args.operation, args.name)
    elif args.command=='doctor':
        from sagaz.services import CORE
        print(json.dumps(CORE.doctor(), ensure_ascii=False, indent=2))
    elif args.command=='credits':
        print(json.dumps(credits(), ensure_ascii=False, indent=2))
    elif args.command=='connect':
        print(json.dumps(connection(), ensure_ascii=False, indent=2))
    elif args.command=='guard':
        print(json.dumps(guard_status(), ensure_ascii=False, indent=2))
    elif args.command == 'god':
        print(json.dumps(public_dict(resolve(args.level)), ensure_ascii=False, indent=2))
    elif args.command == 'discord':
        memory = DiscordMemory(args.db)
        if args.operation == 'stats':
            result = memory.summary()
        elif args.operation == 'search':
            if not args.value: parser.error('discord search exige um termo')
            result = memory.search(args.value)
        else:
            if not args.value: parser.error('discord ingest exige um arquivo JSON')
            result = {'ingested': memory.ingest(load_json(args.value), consent=args.consent)}
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command=='pix':
        print(static_brcode(amount=args.amount))
    elif args.command=='compat':
        print(markdown(compare_directories(args.upstream, args.local)))
    elif args.command=='gateway':
        worker = Gateway(ROOT/'projects/sagaz')
        if args.operation=='cost':
            data=worker.cost.report()
        elif args.operation=='audit-verify':
            data=worker.audit.verify()
        elif args.operation=='audit-checkpoint':
            data=worker.audit.checkpoint()
        elif args.operation=='models':
            data=worker.models()
        else:
            from sagaz.gateway.policy import LOCAL_UI
            data=worker.capability(LOCAL_UI)
        print(json.dumps(data, ensure_ascii=False, indent=2))
    return 0
