#!/usr/bin/env python3
"""Validate planning structure; visual quality and semantic continuity still need review."""
import argparse,json,math
from pathlib import Path

def validate(p):
    e=[]
    def need(ok,msg):
        if not ok:e.append(msg)
    def integer(v):return type(v) is int
    for k in ['id','canon_version','desire','obstacle','resolution','seed','video','scenes','assets','audio']:
        need(k in p,f'Campo ausente: {k}')
    if e:return e
    v=p['video'];fps=v.get('fps');total=v.get('durationInFrames')
    need(integer(fps) and fps>0,'fps inválido');need(integer(total) and total>0,'durationInFrames inválido')
    need(all(integer(v.get(k)) and v[k]>0 for k in ['width','height']),'dimensões inválidas')
    need(integer(p['seed']),'seed deve ser inteiro');need(bool(p['scenes']),'episódio sem cenas')
    need(all(isinstance(p[k],str) and p[k].strip() for k in ['id','canon_version','desire','obstacle','resolution']),'identificação ou história vazia')
    ids=set();cursor=0;prev=None
    for s in p['scenes']:
        sid=s.get('id','?');a=s.get('startFrame');b=s.get('endFrame')
        need(sid not in ids,f'{sid}: id repetido');ids.add(sid)
        if not (integer(a) and integer(b) and b>a):e.append(f'{sid}: intervalo inválido');continue
        need(a==cursor,f'{sid}: lacuna/sobreposição');cursor=b
        for k in ['action','camera','emotion','state_in','state_out']:
            need(bool(s.get(k)),f'{sid}: {k} vazio')
        if prev is not None and s.get('state_in')!=prev:
            need(bool(s.get('transition_reason')),f'{sid}: estado muda sem transição declarada')
        prev=s.get('state_out')
        for cue in s.get('audio_cues',[]):
            at=cue.get('frame');end=cue.get('endFrame',at)
            need(integer(at) and integer(end) and a<=at<end<=b,f'{sid}: cue fora da cena ou duração zero')
        need(isinstance(s.get('narration'),str),f'{sid}: narração ausente, usar string vazia para atuação')
    need(cursor==total,'soma de frames diferente da composição')
    for a in p['assets']:
        need(bool(a.get('id')),'asset sem id')
        need(a.get('rights_status') in ['original','licensed','public_domain'],'asset com direitos pendentes')
        if a.get('rights_status')!='original':need(bool(a.get('license_evidence')),'asset externo sem evidência de licença')
    aud=p['audio'];need(aud.get('reference_status') in ['pending_reference','metadata_only','analyzed','not_needed'],'status de referência sonora inválido')
    need(aud.get('generation_cost')==0,'pipeline exige custo de geração zero')
    if aud.get('voice_required') and aud.get('status')=='ready':
        need(bool(aud.get('voice_path')) and aud.get('timing_status')=='measured','voz marcada pronta sem arquivo/tempo medido')
    return e
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('episode',type=Path);p=a.parse_args()
    try: errors=validate(json.loads(p.episode.read_text()))
    except (KeyError,TypeError,ValueError) as ex:errors=[f'Contrato inválido: {ex}']
    if errors:print('\n'.join(errors));raise SystemExit(1)
    print('Contrato válido; revisão visual/sonora e cânone ainda necessários.')
