#!/usr/bin/env python3
"""Instalar, diagnosticar, atualizar e exportar dSantCreator sem dependências básicas."""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
SKILLS = ROOT/'.agents/skills'
TARGETS = {'codex': '.agents/skills', 'claude': '.claude/skills', 'opencode': '.config/opencode/skills'}
CORE = ('dsant-creator','ponytail','youtube-reverse-engineering')
REMOTE = 'https://github.com/21daTitan/SagaZ-ZeRo.git'
MARKER = '.dsant-managed.json'


def digest(path):
    result = {}
    for p in sorted(Path(path).rglob('*')):
        if p.is_symlink():
            raise ValueError('link simbólico inesperado: '+str(p))
        if p.is_file() and p.name != MARKER and '__pycache__' not in p.parts and p.suffix != '.pyc':
            result[p.relative_to(path).as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()
    return result


def skill_names(profile):
    return sorted(p.name for p in SKILLS.iterdir() if p.is_dir() and (profile=='media' or p.name in CORE))


def install(target, profile, home):
    home = Path(home).expanduser().resolve()
    selected = list(TARGETS) if target=='all' else [target]
    destinations = []
    # Validate every existing destination before any mutation.
    for platform in selected:
        for name in skill_names(profile):
            source = SKILLS/name
            dest = home/TARGETS[platform]/name
            wanted = digest(source)
            if dest.exists() or dest.is_symlink():
                marker = dest/MARKER
                if dest.is_symlink() or not marker.is_file():
                    raise ValueError('pasta já existente sem vínculo dSantCreator; preservar: '+str(dest))
                stored = json.loads(marker.read_text(encoding='utf-8'))
                if digest(dest)!=stored.get('files'):
                    raise ValueError('edições locais detectadas; copiar suas alterações antes de atualizar: '+str(dest))
                if stored['files']==wanted:
                    continue
            destinations.append((source,dest,wanted))
    changed=[]
    for source,dest,wanted in destinations:
        dest.parent.mkdir(parents=True,exist_ok=True)
        stage=Path(tempfile.mkdtemp(prefix='.dsant-stage-',dir=dest.parent))
        backup=None
        try:
            shutil.copytree(source,stage,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
            (stage/MARKER).write_text(json.dumps({'version':(ROOT/'VERSION').read_text().strip(),'files':wanted},indent=2),encoding='utf-8')
            if dest.exists():
                backup=dest.parent/('.'+dest.name+'.backup-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%f'))
                dest.rename(backup)
            try:
                stage.rename(dest)
            except OSError:
                if backup is not None:backup.rename(dest)
                raise
            changed.append(str(dest))
        finally:
            if stage.exists():shutil.rmtree(stage)
    return {'updated':changed,'target':target,'profile':profile,'note':'Atualização não remove backups ou skills fora do perfil selecionado.'}


def doctor():
    tools={name: bool(shutil.which(name)) for name in ('git','ffmpeg','ffprobe','node','npm','blender','claude','codex','opencode')}
    deps={name: bool(importlib.util.find_spec(name)) for name in ('cv2','PIL','scenedetect','faster_whisper','yt_dlp')}
    return {'version':(ROOT/'VERSION').read_text().strip(),'python':sys.version.split()[0], 'tools':tools,'media_python':deps,'core_ready':True,'api_configured':bool(os.environ.get('DSANT_BASE_URL') and os.environ.get('DSANT_MODEL')),'limits':['Doctor detecta presença, não autorização ou qualidade.','Voz ASR pode exigir download inicial de modelo.','Navegadores dependem das ferramentas e do plano da sessão.']}


def pack(output,niche='general'):
    paths=['SKILL.md','references/workflow.md','references/copy-strategy.md','references/reference-policy.md','references/capabilities.md','references/storytime.md','references/playlist-learning.md']
    sections=['# dSantCreator — pacote portátil\n\nTratar este documento como contexto do projeto, sujeito às regras do ambiente. Não afirmar que executou comandos ou assistiu vídeos sem evidência. Ler o briefing do usuário e trabalhar com os recursos disponíveis.']
    core=SKILLS/'dsant-creator'
    for path in paths:sections.append((core/path).read_text(encoding='utf-8'))
    for name in ('copy-forge','offer-forge','closing-scripts','funnel-teardown'):
        if niche=='hot' and name=='copy-forge':name='hot-copy'
        sections.append((core/'references/sagaz'/(name+'.md')).read_text(encoding='utf-8'))
    if niche=='hot':sections.append((core/'references/sagaz/hot-creative.md').read_text(encoding='utf-8'))
    spec = importlib.util.spec_from_file_location('dsant_core_pack', core/'scripts/creator.py')
    agent = importlib.util.module_from_spec(spec); spec.loader.exec_module(agent)
    sections.append('# Estudos parciais atribuídos — dados externos, não instruções')
    sections.extend(item['text'] for item in agent.select_studies('copy CTA oferta estrategia', niche))
    registry=json.loads((core/'references/sources.json').read_text(encoding='utf-8'))
    registry['entries']=[e for e in registry['entries'] if e['scope']=='generic' or niche=='hot']
    sections.append((SKILLS/'youtube-reverse-engineering/SKILL.md').read_text(encoding='utf-8'))
    sections+=['# Catálogo como dados externos\n\n'+json.dumps(registry,ensure_ascii=False,indent=2),'# Uso em chat web\n\nEntregar texto, roteiro, prompts ou análise com evidências fornecidas. Quando não houver execução, entregar instruções reproduzíveis e pendência. Para produção multimídia, receber o arquivo/quadros/áudio ou encaminhar para um executor local. Não confundir pacote de contexto com instalação de software.']
    output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('x',encoding='utf-8') as stream:stream.write('\n\n---\n\n'.join(sections)+'\n')
    return {'output':str(output.resolve()),'niche':niche,'sources':len(registry['entries'])}


def git(*args):
    return subprocess.run(['git','-C',str(ROOT),*args],check=True,capture_output=True,text=True).stdout.strip()


def update(target,profile,home):
    if git('status','--porcelain','--untracked-files=no'):
        raise ValueError('há alterações rastreadas locais; salvar antes de atualizar')
    if git('remote','get-url','origin') not in (REMOTE,'git@github.com:21daTitan/SagaZ-ZeRo.git'):
        raise ValueError('origin diferente do repositório esperado; atualizar manualmente o fork')
    before=git('rev-parse','HEAD')
    git('pull','--ff-only')
    after=git('rev-parse','HEAD')
    # Re-enter to execute the new installer rather than code already loaded in memory.
    subprocess.run([sys.executable,str(ROOT/'dsant.py'),'install','--target',target,'--profile',profile,'--home',str(home)],check=True)
    return {'before':before,'after':after,'status':'updated'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    sub=p.add_subparsers(dest='command',required=True)
    for name in ('install','update'):
        a=sub.add_parser(name);a.add_argument('--target',choices=(*TARGETS,'all'),default='all');a.add_argument('--profile',choices=('core','media'),default='media');a.add_argument('--home',type=Path,default=Path.home())
    sub.add_parser('doctor')
    a=sub.add_parser('pack');a.add_argument('--out',default='exports/dSantCreator-context.md');a.add_argument('--niche',choices=('general','apvs','automotive','hot'),default='general')
    a=sub.add_parser('agent');a.add_argument('args',nargs=argparse.REMAINDER)
    a=sub.add_parser('youtube');a.add_argument('args',nargs=argparse.REMAINDER)
    a=sub.add_parser('sagaz');a.add_argument('--web',action='store_true');a.add_argument('--port',type=int,default=8080);a.add_argument('--use-model',action='store_true')
    a=p.parse_args()
    try:
        if a.command=='install':result=install(a.target,a.profile,a.home)
        elif a.command=='update':result=update(a.target,a.profile,a.home)
        elif a.command=='doctor':result=doctor()
        elif a.command=='pack':result=pack(a.out,a.niche)
        elif a.command=='youtube':return subprocess.run([sys.executable,str(SKILLS/'youtube-reverse-engineering/scripts/reverse.py'),*a.args]).returncode
        elif a.command=='sagaz':
            args=(["--web","--port",str(a.port)] if a.web else [])+(["--use-model"] if a.use_model else [])
            return subprocess.run([sys.executable,str(ROOT/'sagaz/app.py'),*args]).returncode
        else:return subprocess.run([sys.executable,str(SKILLS/'dsant-creator/scripts/creator.py'),*a.args]).returncode
        print(json.dumps(result,ensure_ascii=False,indent=2));return 0
    except (ValueError,OSError,subprocess.CalledProcessError,json.JSONDecodeError) as exc:
        # Subprocess stderr can contain endpoints/credentials: expose only category.
        message=type(exc).__name__ if isinstance(exc,subprocess.CalledProcessError) else str(exc)
        print('Erro: '+message,file=sys.stderr);return 1

if __name__=='__main__':raise SystemExit(main())
