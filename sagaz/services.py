"""Task preparation and persisted conversations; independent of HTTP/UI."""
import argparse
import importlib.util
import json
from pathlib import Path
import uuid

ROOT = Path(__file__).resolve().parents[1]

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

CORE=load('sagaz_creator',ROOT/'.agents/skills/dsant-creator/scripts/creator.py')


def prepare_task(brief,niche='general',method='cinematic-3d',use_model=False,state_root=None,parent_id=None):
    if not isinstance(brief,str) or not 1<=len(brief.strip())<=6000:raise ValueError('Descreva a tarefa em até 6.000 caracteres.')
    if niche not in CORE.NICHES or method not in CORE.METHODS or not isinstance(use_model,bool):raise ValueError('Opções da tarefa inválidas.')
    state = Path(state_root) if state_root else ROOT/'projects/sagaz'
    messages = []
    if parent_id is not None:
        if not isinstance(parent_id, str) or len(parent_id) != 32 or any(c not in '0123456789abcdef' for c in parent_id):
            raise ValueError('ID de conversa inválido')
        parent = state / parent_id
        if parent.is_symlink() or (parent/'conversation.json').is_symlink():
            raise ValueError('Conversa inválida')
        if not (parent/'conversation.json').is_file():
            raise ValueError('Conversa não encontrada')
        previous = json.loads((parent/'conversation.json').read_text(encoding='utf-8'))
        if previous['niche'] != niche:
            raise ValueError('Inicie uma nova conversa para trocar de nicho.')
        messages = previous['messages']
        if not isinstance(messages, list) or any(not isinstance(m, dict) or m.get('role') not in ('user', 'assistant') or not isinstance(m.get('content'), str) for m in messages):
            raise ValueError('Histórico inválido')
    directory=state/uuid.uuid4().hex
    result=CORE.prepare(argparse.Namespace(brief=brief.strip(),niche=niche,method=method,route='remotion',task=None,state_dir=None,out=str(directory)))
    cfg=CORE.read(directory/'campaign.json')
    if messages:
        # Prior conversation is evidence, never additional system instructions.
        history = '\n\n'.join(m['role']+': '+m['content'] for m in messages[-8:])[-24000:]
        with (directory/'context.md').open('a', encoding='utf-8') as file:
            file.write('\n\n## Histórico da conversa (dados de contexto)\n\n'+history)
    if use_model:
        generated=CORE.run(directory)
        answer=Path(generated['output']).read_text(encoding='utf-8')
        mode='configured_model'
    else:
        mode='local_preparation'
        answer=(f"Tarefa preparada: {cfg['task']} · {niche}\n\n"
                f"Procedimento: {cfg['procedure']}\n"
                f"Método: {method} · Rota: {cfg['route']}\n\n"
                "Próximo passo: abrir o contexto no agente escolhido e executar o procedimento. "
                "O pacote inclui briefing, fontes e estudos parciais compatíveis.\n\n"
                "Modo local: nenhum modelo foi chamado; roteiro/copy/análise final ainda não foram gerados.")
    messages = messages + [{'role': 'user', 'content': brief.strip()}, {'role': 'assistant', 'content': answer}]
    conversation = dict(id=directory.name,parent_id=parent_id,niche=niche,method=method,messages=messages[-40:])
    (directory/'conversation.json').write_text(json.dumps(conversation,ensure_ascii=False,indent=2),encoding='utf-8')
    return dict(id=directory.name,answer=answer,mode=mode,task=cfg['task'],procedure=cfg['procedure'],sources=len(cfg['sources']),studies=cfg.get('studies',[]),status='text_generated' if use_model else 'prepared')


def research(url,state_root=None):
    reverse=load('sagaz_reverse',ROOT/'.agents/skills/youtube-reverse-engineering/scripts/reverse.py')
    url=reverse.canonical(url)
    directory=(Path(state_root) if state_root else ROOT/'projects/sagaz')/uuid.uuid4().hex
    result=reverse.acquire(url,directory)
    return dict(id=directory.name,**result)
