#!/usr/bin/env python3
"""Evidence intake and dossier checks; no paid API, no fabricated analysis."""
import argparse
from datetime import datetime, timezone
import hashlib
import html
import importlib.util
import json
import math
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import parse_qs, urlparse

ROOT=Path(__file__).resolve().parents[1]
SCORES=('hook','promise','pace','retention','value','proof','originality','cta','audience','editorial_potential')


def canonical(url):
    p=urlparse(url)
    if p.scheme!='https' or p.username or p.password or p.port not in (None,443):raise ValueError('URL HTTPS YouTube inválida')
    parts=p.path.strip('/').split('/')
    if p.hostname=='youtu.be':ident=parts[0] if len(parts)==1 else ''
    elif p.hostname in ('youtube.com','www.youtube.com','m.youtube.com'):
        ident=parse_qs(p.query).get('v',[''])[0] if p.path=='/watch' else parts[1] if len(parts)==2 and parts[0] in ('shorts','live','embed') else ''
    else:raise ValueError('host não autorizado')
    if not re.fullmatch(r'[A-Za-z0-9_-]{11}',ident):raise ValueError('usar URL de um vídeo; playlists são estudadas por aula')
    return 'https://www.youtube.com/watch?v='+ident


def number(value):
    return isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value)


def timestamp(value):
    total=0.0
    for part in value.replace(',','.').split(':'):total=total*60+float(part)
    return total


def parse_transcript(path):
    path=Path(path); raw=path.read_text(encoding='utf-8-sig');segments=[]
    if path.suffix.lower() in ('.json','.json3'):
        data=json.loads(raw)
        if isinstance(data,dict) and 'events' in data:
            for event in data['events']:
                if not event.get('segs'):continue
                start=event.get('tStartMs',0)/1000;end=start+event.get('dDurationMs',0)/1000
                text=''.join(s.get('utf8','') for s in event['segs']).strip()
                segments.append({'start':start,'end':end,'text':text})
        elif isinstance(data,list):segments=data
        else:segments=data.get('segments',[])
    else:
        lines=raw.splitlines();i=0
        while i<len(lines):
            if '-->' not in lines[i]:i+=1;continue
            first,last=lines[i].split('-->',1);start=timestamp(first.strip());end=timestamp(last.strip().split()[0]);i+=1;text=[]
            while i<len(lines) and lines[i].strip():text.append(lines[i]);i+=1
            body=html.unescape(re.sub(r'<[^>]+>','',' '.join(text)))
            segments.append({'start':start,'end':end,'text':body})
    clean=[]
    for s in segments:
        a=s.get('start');b=s.get('end');text=s.get('text')
        if not number(a) or not number(b) or a<0 or b<=a or not isinstance(text,str):raise ValueError('segmento inválido')
        if text.strip():clean.append({'start':a,'end':b,'text':text.strip()})
    clean.sort(key=lambda s:s['start'])
    return clean


def write(path,data):
    Path(path).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def acquire(url,out,transcript=None,metadata=None):
    url=canonical(url) if url else None
    if url is None and not transcript and not metadata:raise ValueError('fornecer URL ou evidência local')
    out=Path(out);out.mkdir(parents=True,exist_ok=False)
    notes=[];meta={};segments=[];original=None
    if metadata:meta=json.loads(Path(metadata).read_text(encoding='utf-8-sig'))
    if transcript:
        segments=parse_transcript(transcript);original=Path(transcript).read_bytes()
    if url and not metadata and not transcript:
        if importlib.util.find_spec('yt_dlp'):
            command=[sys.executable,'-m','yt_dlp','--skip-download','--write-info-json','--write-subs','--write-auto-subs','--sub-langs','pt-orig,pt,en','--sub-format','json3/vtt','--socket-timeout','15','--retries','0','--extractor-retries','0','--no-playlist','-o',str(out/'source.%(ext)s'),url]
            try:
                result=subprocess.run(command,capture_output=True,text=True,timeout=120)
                if result.returncode:notes.append('yt-dlp falhou; coleta incompleta, sem publicar detalhes de credenciais')
            except subprocess.TimeoutExpired:notes.append('yt-dlp excedeu 120 s')
            info=out/'source.info.json'
            if info.exists():meta=json.loads(info.read_text(encoding='utf-8'))
            options=sorted(list(out.glob('*.json3'))+list(out.glob('*.vtt')))
            if options:
                chosen=next((p for p in options if '.pt-orig.' in p.name),options[0])
                segments=parse_transcript(chosen);original=chosen.read_bytes()
        else:notes.append('yt-dlp ausente; instalar em venv ou fornecer legenda/metadata local')
    duration=meta.get('duration')
    if number(duration) and duration>10800:notes.append('Duração acima de 3 h; definir escopo antes de aprofundar')
    if not segments:notes.append('Sem fala verificável; modo metadata/degradado, não afirmar análise integral')
    dossier=json.loads((ROOT/'references/dossier-template.json').read_text(encoding='utf-8'))
    dossier['source'].update(url=url,title=meta.get('title'),channel=meta.get('channel') or meta.get('uploader'),duration_seconds=duration,views=meta.get('view_count'),upload_date=meta.get('upload_date'))
    dossier['evidence'].update(transcript=bool(segments),coverage='transcript_only_unreviewed' if segments else 'metadata_only',limitations=notes+['Cortes, câmera, B-roll e áudio não inspecionados pelo coletor.'])
    write(out/'transcript.json',segments)
    write(out/'dossier.json',dossier)
    write(out/'evidence.json',{'collected_at':datetime.now(timezone.utc).isoformat(),'url':url,'transcript_sha256':hashlib.sha256(original).hexdigest() if original else None,'segments':len(segments),'limitations':notes})
    return {'directory':str(out.resolve()),'status':'draft','segments':len(segments),'next':'Revisar evidências e preencher dossier.json; depois executar validate.','limitations':notes}


def validate(data):
    if data.get('status') not in ('draft','reviewed'):raise ValueError('status inválido')
    if data['source'].get('url') is not None:canonical(data['source']['url'])
    if set(data['scorecard'])!=set(SCORES):raise ValueError('scorecard exige dez critérios')
    values=[]
    for item in data['scorecard'].values():
        score=item['score']
        if score is not None:
            if not number(score) or not 0<=score<=10 or not item.get('reason','').strip():raise ValueError('nota sem justificativa válida')
            values.append(score)
    if not all(isinstance(data['evidence'].get(key),bool) for key in ('transcript','visual','audio')):raise ValueError('modalidades de evidência devem ser booleanas')
    duration=data['source'].get('duration_seconds');last=0
    if duration is not None and (not number(duration) or duration<=0):raise ValueError('duração inválida')
    for beat in data['beats']:
        a,b=beat['start'],beat['end']
        if not number(a) or not number(b) or a<last or b<=a or (duration is not None and b>duration):raise ValueError('intervalos inválidos ou sobrepostos')
        if not beat.get('function') or not beat.get('evidence'):raise ValueError('beat sem função/evidência')
        last=b
    if not data['evidence'].get('visual'):
        if any(b.get('cuts_per_second') is not None for b in data['beats']):raise ValueError('densidade de cortes exige evidência visual')
    if data['status']=='reviewed':
        if not any(data['evidence'].get(key) for key in ('transcript','visual','audio')):raise ValueError('revisão exige evidência disponível')
        if not data['beats'] or not data['blueprint'] or not data['mechanism'] or not data['verdict']:raise ValueError('dossiê revisado incompleto')
        if len(data['variations'])!=3:raise ValueError('fornecer três variações originais')
    return {'valid':True,'status':data['status'],'editorial_average':round(sum(values)/len(values),2) if values else None,'score_coverage':f'{len(values)}/10','limit':'Checagem estrutural; sem previsão de CTR ou validação de veracidade.'}


def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    a=sub.add_parser('acquire');a.add_argument('url',nargs='?');a.add_argument('--out',required=True);a.add_argument('--transcript');a.add_argument('--metadata')
    a=sub.add_parser('validate');a.add_argument('file')
    args=p.parse_args()
    try:
        result=acquire(args.url,args.out,args.transcript,args.metadata) if args.command=='acquire' else validate(json.loads(Path(args.file).read_text(encoding='utf-8')))
        print(json.dumps(result,ensure_ascii=False,indent=2));return 0
    except (ValueError,OSError,KeyError,TypeError) as exc:
        print('Erro: '+str(exc),file=sys.stderr);return 1

if __name__=='__main__':raise SystemExit(main())
