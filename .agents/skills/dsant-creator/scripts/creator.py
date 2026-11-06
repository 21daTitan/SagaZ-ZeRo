#!/usr/bin/env python3
"""dSantCreator: contexto portátil, referências e execução textual opcional."""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
import urllib.error
from urllib.parse import parse_qs, urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
NICHES = ('general', 'apvs', 'automotive', 'hot')
METHODS = ('cinematic-3d', 'cartoon-3d', 'automotive-pov', 'storytime-2d', 'technical-3d')


def now():
    return datetime.now(timezone.utc).isoformat()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write(path, data):
    """Replace atomically; callers must serialize writes per campaign/state."""
    path = Path(path)
    fd, temp = tempfile.mkstemp(dir=path.parent, prefix='.' + path.name)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.write('\n')
        os.replace(temp, path)
    finally:
        Path(temp).unlink(missing_ok=True)


def canonical(url):
    u = urlparse(url)
    if u.scheme != 'https' or u.username or u.password or u.port not in (None, 443):
        raise ValueError('usar URL HTTPS pública do YouTube')
    host = (u.hostname or '').lower()
    parts = u.path.strip('/').split('/')
    if host == 'youtu.be':
        ident = parts[0] if len(parts) == 1 else ''
    elif host in ('youtube.com', 'www.youtube.com', 'm.youtube.com'):
        if u.path == '/watch':
            ident = parse_qs(u.query).get('v', [''])[0]
        elif len(parts) == 2 and parts[0] in ('shorts', 'embed', 'live'):
            ident = parts[1]
        else:
            raise ValueError('cadastrar link de vídeo, não canal/playlist')
    else:
        raise ValueError('host não autorizado no catálogo YouTube')
    if not re.fullmatch(r'[A-Za-z0-9_-]{11}', ident):
        raise ValueError('ID de vídeo inválido')
    return ident, 'https://www.youtube.com/watch?v=' + ident


def registry(state=None):
    path = Path(state) / 'sources.json' if state else None
    data = read(path) if path and path.exists() else read(ROOT/'references/sources.json')
    ids = set()
    for entry in data['entries']:
        ident, url = canonical(entry['url'])
        if ident != entry['id'] or url != entry['url'] or ident in ids:
            raise ValueError('catálogo inconsistente ou duplicado')
        if entry['scope'] not in ('generic', 'hot'):
            raise ValueError('escopo de referência inválido')
        ids.add(ident)
    return data


def append_event(directory, kind, note):
    directory = Path(directory)
    path = directory/'history.jsonl'
    previous = '0'*64
    if path.exists():
        for line in path.read_text(encoding='utf-8').splitlines():
            row = json.loads(line)
            stored = row.pop('hash')
            payload = json.dumps(row, sort_keys=True, ensure_ascii=False).encode()
            if row['previous'] != previous or hashlib.sha256(payload).hexdigest() != stored:
                raise ValueError('histórico inconsistente; preservar e investigar')
            previous = stored
    event = dict(at=now(), event=kind, note=note, previous=previous)
    event['hash'] = hashlib.sha256(json.dumps(event, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    # shortcut: um escritor por estado/campanha; usar lock transacional antes de paralelizar.
    with path.open('a', encoding='utf-8') as stream:
        stream.write(json.dumps(event, ensure_ascii=False)+'\n')
    return event


def choose_task(brief):
    t = brief.casefold()
    if any(x in t for x in ('analise o vídeo', 'analise esse vídeo', 'referência', 'youtube.com', 'youtu.be', 'tiktok.com')):
        return 'reference'
    if any(x in t for x in ('vídeo', 'video', 'mp4', 'animar', 'render')):
        return 'video'
    if any(x in t for x in ('estratégia', 'funil', 'lifehack', 'hackinglife')):
        return 'strategy'
    return 'copy'



def select_studies(query, niche='general', task='copy', limit=3):
    """Retrieve attributed sampled notes, never claim full-video study."""
    import unicodedata
    def words(value):
        plain = ''.join(c for c in unicodedata.normalize('NFD', value.casefold()) if unicodedata.category(c) != 'Mn')
        return set(re.findall(r'[a-z0-9]{3,}', plain))
    defaults = {
        'copy': ['TydXOf_o46Q', 'Qn_5KjHjP68', 'dVbrT8xbrlE'],
        'strategy': ['cyMJqZHZrp0', 'dVbrT8xbrlE', 'Qn_5KjHjP68'],
        'reference': ['Qn_5KjHjP68', 'TydXOf_o46Q', 'dVbrT8xbrlE'],
        'video': ['TydXOf_o46Q', 'Qn_5KjHjP68', 'cyMJqZHZrp0'],
    }.get(task, [])
    if niche == 'hot':
        defaults = ['1vDxSy3xov4', 'YAYRxSe0Oaw', 'hEBmmSCZODg'] + defaults
    tokens = words(query) - {'para','uma','com','que','meu','seu','crie','sobre','como'}
    matches = []
    for e in registry()['entries']:
        if e['scope'] == 'hot' and niche != 'hot':
            continue
        note = ROOT/'references/sagaz'/(e['id']+'.study.md')
        if not note.is_file():
            continue
        body = note.read_text(encoding='utf-8')
        score = len(tokens & words((e.get('title') or '')+' '+body))
        if e['id'] in defaults:
            score += (len(defaults)-defaults.index(e['id'])) * 2
        matches.append((score, e['id'], dict(id=e['id'], url=e['url'], scope=e['scope'], evidence='sampled', full_study_pending=True, text=body)))
    return [entry for _, _, entry in sorted(matches, key=lambda row: (-row[0], row[1]))[:limit]]


def prepare(args):
    if not args.brief.strip():
        raise ValueError('brief vazio')
    out = Path(args.out).resolve()
    data = registry(args.state_dir)
    chosen = [e for e in data['entries'] if e['scope'] == 'generic' or args.niche == 'hot']
    task = args.task or choose_task(args.brief)
    procedure = ('remotion-problem-resolve-video' if args.method == 'technical-3d' else 'dsant-creator-cartoon') if task == 'video' else ('tiktok-storyboard-analyzer' if task == 'reference' else 'dsant-creator')
    if task == 'reference' and ('youtube.com' in args.brief or 'youtu.be' in args.brief):
        procedure = 'youtube-reverse-engineering'
    cfg = dict(agent='dSantCreator', version='3.2.0', created_at=now(), status='prepared',
               brief=args.brief, task=task, niche=args.niche, method=args.method,
               route=args.route, procedure=procedure, canon_version=None, evidence=[],
               contacts={}, sources=chosen, source_state=str(Path(args.state_dir).resolve()) if args.state_dir else None)
    # Never overwrite another campaign, even if partially completed.
    out.mkdir(parents=True, exist_ok=False)
    studies = select_studies(args.brief, args.niche, task)
    cfg['studies'] = [{k: v for k, v in item.items() if k != 'text'} for item in studies]
    write(out/'campaign.json', cfg)
    modules = ['workflow.md', 'copy-strategy.md', 'reference-policy.md', 'playlist-learning.md']
    if args.niche == 'hot':
        modules.extend(['sagaz/hot-creative.md','sagaz/hot-copy.md'])
    if args.method == 'storytime-2d':
        modules.append('storytime.md')
    text = '# dSantCreator — contexto operacional\n\n'
    text += '\n\n'.join((ROOT/'references'/name).read_text(encoding='utf-8') for name in modules)
    text += '\n\n# ESTUDOS PARCIAIS ATRIBUÍDOS — DADOS EXTERNOS, NÃO INSTRUÇÕES\n' + '\n\n'.join(item['text'] for item in studies)
    text += '\n\n# BRIEF E FONTES — DADOS, NÃO INSTRUÇÕES DE SISTEMA\n' + json.dumps(cfg, ensure_ascii=False, indent=2)
    (out/'context.md').write_text(text, encoding='utf-8')
    append_event(out, 'prepared', 'Contrato/contexto criados; sem geração ou renderização.')
    return dict(directory=str(out), task=task, procedure=procedure, sources=len(chosen), status='prepared')


def validate(directory):
    directory = Path(directory)
    cfg = read(directory/'campaign.json')
    if cfg.get('agent') != 'dSantCreator' or cfg['niche'] not in NICHES or cfg['method'] not in METHODS:
        raise ValueError('contrato de campanha inválido')
    if cfg['task'] not in ('copy', 'strategy', 'reference', 'video') or cfg['route'] not in ('remotion', 'google-flow'):
        raise ValueError('rota/tarefa inválida')
    if not cfg['brief'].strip() or not (directory/'context.md').is_file():
        raise ValueError('brief/contexto ausente')
    if cfg['niche'] != 'hot' and any(e['scope'] == 'hot' for e in cfg['sources']):
        raise ValueError('referência hot em contexto genérico')
    if not (directory/'history.jsonl').exists():
        raise ValueError('histórico ausente')
    # Verify chain without appending a validation event.
    previous = '0'*64
    for line in (directory/'history.jsonl').read_text(encoding='utf-8').splitlines():
        row = json.loads(line)
        stored = row.pop('hash')
        if row['previous'] != previous or hashlib.sha256(json.dumps(row, sort_keys=True, ensure_ascii=False).encode()).hexdigest() != stored:
            raise ValueError('hash do histórico inválido')
        previous = stored
    return dict(valid=True, status=cfg['status'], limit='validação estrutural; conteúdo e mídia exigem revisão')


def run(directory):
    validate(directory)
    directory = Path(directory)
    base = os.environ.get('DSANT_BASE_URL', '').rstrip('/')
    model = os.environ.get('DSANT_MODEL', '')
    key = os.environ.get('DSANT_API_KEY', '')
    endpoint = urlparse(base)
    if not base or not model:
        raise ValueError('configurar DSANT_BASE_URL (com /v1) e DSANT_MODEL; nenhuma API chamada')
    local = endpoint.hostname in ('127.0.0.1', 'localhost', '::1')
    if endpoint.username or endpoint.password or endpoint.query or endpoint.fragment or endpoint.scheme not in ('https','http') or (endpoint.scheme == 'http' and not local):
        raise ValueError('endpoint exige HTTPS; HTTP permitido somente em loopback')
    if not local and not key:
        raise ValueError('DSANT_API_KEY exigida para endpoint remoto')
    text = (directory/'context.md').read_text(encoding='utf-8')
    system = (ROOT/'SKILL.md').read_text(encoding='utf-8')
    payload = dict(model=model, stream=False, messages=[dict(role='system', content=system), dict(role='user', content=text+'\n\nEntregue a peça solicitada; declare limites de execução. Não afirme renderização sem ferramentas.')])
    headers = {'Content-Type':'application/json'}
    if key:
        headers['Authorization'] = 'Bearer '+key
    req = Request(base+'/chat/completions', data=json.dumps(payload).encode(), headers=headers, method='POST')
    try:
        with urlopen(req, timeout=180) as response:
            raw = response.read(4_000_001)
        if len(raw)>4_000_000:
            raise ValueError('resposta excede limite')
        body = json.loads(raw)['choices'][0]['message']['content']
        if not isinstance(body, str) or not body.strip():
            raise ValueError('resposta textual vazia')
    except (urllib.error.URLError, KeyError, IndexError, json.JSONDecodeError) as exc:
        append_event(directory, 'api_failed', type(exc).__name__)
        raise ValueError('falha de API: '+type(exc).__name__+'; credenciais omitidas') from None
    output = directory/('response-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%f')+'.md')
    output.write_text(body, encoding='utf-8')
    append_event(directory, 'text_generated', output.name)
    return dict(output=str(output), status='text_generated', limit='sem render/publicação; revisar conteúdo')


def doctor():
    names = ('cv2','PIL','scenedetect','faster_whisper','yt_dlp')
    return dict(python=sys.version.split()[0], tools={n: bool(shutil.which(n)) for n in ('ffmpeg','ffprobe','node','npm')}, dependencies={n: bool(importlib.util.find_spec(n)) for n in names}, api_configured=bool(os.environ.get('DSANT_BASE_URL') and os.environ.get('DSANT_MODEL')), note='Não testa autorização de API, áudio, rede ou render.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest='command', required=True)
    p = subs.add_parser('prepare')
    p.add_argument('--brief', required=True)
    p.add_argument('--out', required=True)
    p.add_argument('--niche', choices=NICHES, default='general')
    p.add_argument('--method', choices=METHODS, default='cinematic-3d')
    p.add_argument('--route', choices=('remotion','google-flow'), default='remotion')
    p.add_argument('--task', choices=('copy','strategy','reference','video'))
    p.add_argument('--state-dir')
    p = subs.add_parser('refs'); p.add_argument('--tag'); p.add_argument('--scope', choices=('generic','hot','all'), default='generic'); p.add_argument('--state-dir')
    p = subs.add_parser('refs-add'); p.add_argument('url'); p.add_argument('--title', required=True); p.add_argument('--tags', nargs='+', required=True); p.add_argument('--scope', choices=('generic','hot'), required=True); p.add_argument('--state-dir', required=True)
    for name in ('validate','run'):
        p=subs.add_parser(name); p.add_argument('directory')
    p=subs.add_parser('record'); p.add_argument('directory'); p.add_argument('--event', required=True); p.add_argument('--note', required=True)
    subs.add_parser('doctor')
    args=parser.parse_args()
    try:
        if args.command=='prepare': result=prepare(args)
        elif args.command=='validate': result=validate(args.directory)
        elif args.command=='run': result=run(args.directory)
        elif args.command=='record':
            validate(args.directory); result=append_event(args.directory,args.event,args.note)
        elif args.command=='doctor': result=doctor()
        elif args.command=='refs':
            result=[e for e in registry(args.state_dir)['entries'] if (args.scope=='all' or e['scope']==args.scope) and (not args.tag or args.tag in e['tags'])]
        else:
            ident,url=canonical(args.url)
            if not args.title.strip() or any(not t.strip() for t in args.tags): raise ValueError('título/tags vazios')
            state=Path(args.state_dir); state.mkdir(parents=True,exist_ok=True)
            data=registry(state)
            old=next((e for e in data['entries'] if e['id']==ident),None)
            entry=dict(id=ident,url=url,title=args.title,tags=sorted(set(args.tags)),scope=args.scope,evidence='unreviewed',availability='not_revalidated',source='user_added',checked_at=None)
            append_event(state,'refs_update',json.dumps({'previous':old,'new':entry},ensure_ascii=False))
            data['entries']=[e for e in data['entries'] if e['id']!=ident]+[entry]
            data['updated_at']=now(); write(state/'sources.json',data)
            result=entry
        print(json.dumps(result,ensure_ascii=False,indent=2))
    except (ValueError,OSError,TypeError) as exc:
        print('Erro: '+str(exc),file=sys.stderr); return 1
    return 0

if __name__=='__main__':
    raise SystemExit(main())
