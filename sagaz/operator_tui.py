"""SagaZ-ZeRo operator console v4: designed for Android Termux, SSH and VPS."""
from __future__ import annotations
import getpass
import json
import os
import shutil
import sys
import textwrap

from sagaz.catalog import connection, skills
from sagaz.cti import search as cti_search, summary as cti_summary
from sagaz.gateway.router import ProviderUnavailable
from sagaz.provider_config import load, save
from sagaz.ai_session import respond

TTY = sys.stdout.isatty() and os.environ.get('TERM', '') != 'dumb' and 'NO_COLOR' not in os.environ
CYAN = '\x1b[38;5;51m' if TTY else ''
PURPLE = '\x1b[38;5;141m' if TTY else ''
DIM = '\x1b[38;5;110m' if TTY else ''
GREEN = '\x1b[38;5;83m' if TTY else ''
RED = '\x1b[38;5;203m' if TTY else ''
BOLD = '\x1b[1m' if TTY else ''
RESET = '\x1b[0m' if TTY else ''


def line(char='─'):
    return char * max(34, min(shutil.get_terminal_size((76, 24)).columns - 3, 78))


def logo():
    cfg = connection()
    status = f"{GREEN}ONLINE / {cfg['model']}{RESET}" if cfg['configured'] else f'{RED}MODELO NÃO CONFIGURADO{RESET}'
    print(f'''\n{CYAN}  ╭{line()}╮
  │ {BOLD}S A G A Z  ·  Z E R O{RESET}{CYAN}
  │{RESET}  HOOLEESH33T   {PURPLE}◆ SYSTEM OPERATOR ◆{RESET}
{CYAN}  ╰{line()}╯{RESET}
  {DIM}Core 3.7+  │  CTI • MCP • Gateway • Conhecimento{RESET}
  Provedor: {status}
  {DIM}Digite /ajuda para comandos. O dSant é um projeto separado.{RESET}\n''')


def show_help():
    print(f'''\n{PURPLE}{BOLD}  CONTROLE / SAGAZ{RESET}
    /status          Diagnóstico legível do núcleo
    /skills          Skills disponíveis
    /cti             Resumo da inteligência cibernética
    /cti Emotet      Buscar no acervo CTI
    /modelo          Mostrar o provedor configurado
    /conectar        Configurar modelo (chave oculta)
    /testar          Testar uma chamada real ao modelo
    /limpar          Iniciar nova conversa
    /web             Como acessar a interface HooLeeSh33t
    /dsant           Estado do conector criativo futuro
    /ajuda           Mostrar comandos
    /sair            Encerrar a sessão

  {DIM}Texto sem '/' vai diretamente para o modelo quando conectado.
  Operações no sistema não são executadas sem autorização.{RESET}\n''')


def show_status():
    provider = connection()
    cti = cti_summary()
    print(f'''\n  {CYAN}NÚCLEO{RESET}      SagaZ-ZeRo / HooLeeSh33t
  {CYAN}PROVEDOR{RESET}    {provider['model'] or 'Não configurado'}
  {CYAN}PROTOCOLO{RESET}   OpenAI-compatible · resposta sem streaming
  {CYAN}CHAVE{RESET}       {'Presente (oculta)' if provider['key_present'] else 'Não informada'}
  {CYAN}VERIFICAÇÃO{RESET} {'Não verificado; use /testar' if provider['configured'] else 'Use /conectar'}
  {CYAN}CTI{RESET}         {cti['records']} registros · {cti['verified']} verificados · somente leitura
  {CYAN}EXECUTOR{RESET}    Somente ferramentas aprovadas / sem shell irrestrito\n''')


def show_skills():
    entries = skills()['entries']
    print(f'\n  {PURPLE}SKILLS INSTALADAS · {len(entries)}{RESET}')
    for item in entries:
        legacy = ' · legado criativo' if item['id'].startswith('dsant-') else ''
        print(f"  {CYAN}◈{RESET} {item['id']}{DIM}{legacy}{RESET}")
    print('  dSant independente: conector reservado para repositório futuro.\n')


def show_cti(term):
    if not term:
        data = cti_summary()
        print(f"\n  {PURPLE}ALFA CTI{RESET}  ·  {data['records']} registros; {data['unverified']} não verificados; leitura local.\n")
        return
    data = cti_search(term, limit=5)
    print(f"\n  {PURPLE}CTI SEARCH{RESET}  ·  {data['count']} resultado(s) para {term!r}")
    for row in data['entries']:
        print(f"\n  {CYAN}{row['knowledge_id']}{RESET} · {row['topic']}")
        summary = row.get('technical_description', '').replace('\n', ' ')
        for part in textwrap.wrap(summary[:300], width=68)[:3]:
            print('  '+part)
        print(f"  {DIM}Fonte: não auditada · estado: unverified{RESET}")
    print()


def connect():
    print(f'\n{PURPLE} CONFIGURAR PROVEDOR{RESET} · sem exibir credenciais')
    current = connection()
    base = input('  Endpoint (/v1, HTTPS ou localhost): ').strip()
    model = input(f"  Modelo [{current.get('model') or 'nome-do-modelo'}]: ").strip() or current.get('model', '')
    key = getpass.getpass('  Chave API (oculta; Enter para endpoint local): ')
    cfg = save(base, model, key)
    print(f'  {GREEN}Configuração salva no usuário local.{RESET}')
    print(f'  Arquivo protegido: {cfg} (0600).')
    print('  Execute /testar para verificar conectividade real.\n')


def chat(text, parent_id=None):
    data = respond(text, parent_id=parent_id)
    print(f'\n{GREEN} SAGA Z ❯{RESET}\n')
    print(textwrap.fill(data['answer'], width=max(40, min(100, shutil.get_terminal_size((86,24)).columns - 4)),
                        replace_whitespace=False, drop_whitespace=False))
    print()
    return data.get('id')


def run(use_model=False):
    try:
        load()
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f'{RED}Configuração protegida rejeitada: {exc}{RESET}', file=sys.stderr)
    logo()
    parent_id = None
    while True:
        try:
            text = input(f'{CYAN} SagaZ{PURPLE} ❯ {RESET}').strip()
        except (EOFError, KeyboardInterrupt):
            print('\n  Sessão encerrada.\n')
            return 0
        if not text:
            continue
        cmd, _, args = text.partition(' ')
        cmd = cmd.casefold()
        try:
            if cmd in ('/sair', '/exit', 'sair', 'exit', 'quit'):
                print('  SagaZ offline.\n')
                return 0
            elif cmd in ('/ajuda', '/help'):
                show_help()
            elif cmd == '/status':
                show_status()
            elif cmd == '/skills':
                show_skills()
            elif cmd == '/cti':
                show_cti(args.strip())
            elif cmd in ('/modelo', '/modelos'):
                info = connection()
                print(f"  Provedor: {info['model'] or '(nenhum)'} · endpoint: {'configurado' if info['configured'] else 'ausente'} · acesso ainda não verificado")
            elif cmd == '/conectar':
                connect()
            elif cmd == '/testar':
                if not connection()['configured']:
                    print('  Configure primeiro com /conectar.')
                else:
                    answer = respond('Teste de conectividade: responda exatamente PONG.')
                    print('  Modelo respondeu:', answer['answer'][:220])
                    print('  Acesso ao provedor confirmado; qualidade ainda não avaliada.')
            elif cmd == '/limpar':
                parent_id = None
                print('  Nova conversa. Histórico anterior preservado em disco.')
            elif cmd == '/web':
                print('  Na VPS, use um túnel SSH para localhost:8080; não exponha a porta sem autenticação adicional.')
            elif cmd == '/dsant':
                print('  dSant-CreaTor: conector reservado, futuro repositório independente. Nenhuma execução.')
            elif cmd == '/criar':
                print('  Comando criativo legado; dSant está sendo separado do SagaZ.')
                from sagaz.services import operator_command
                print(operator_command(text, use_model=use_model)['answer'])
            elif cmd.startswith('/'):
                print('  Comando desconhecido. Use /ajuda. Nenhuma tarefa foi executada.')
            elif not connection()['configured']:
                print('  O núcleo está pronto, mas não existe IA conectada. Use /conectar para conversar de verdade.')
            else:
                parent_id = chat(text, parent_id=parent_id)
        except (ValueError, OSError, ProviderUnavailable, json.JSONDecodeError, TypeError) as exc:
            detail = type(exc).__name__ if isinstance(exc, OSError) else str(exc)
            print(f'  {RED}Não foi possível executar: {detail}{RESET}')
    return 0
