"""Real SagaZ conversational path, routed through existing audited Gateway."""
from __future__ import annotations
import json
from pathlib import Path
import re
import uuid

from sagaz.gateway.policy import LOCAL_UI
from sagaz.gateway.service import Gateway

SYSTEM = (
    'Você é SagaZ-ZeRo, operador HooLeeSh33t by dSant. Responda em português de forma técnica, '
    'direta e acionável. Preserve os créditos históricos à Cassandra sem se apresentar como ela. '
    'Diferencie planos de ações executadas; não invente acesso a arquivos, rede, shell ou VPS. '
    'Ferramentas e alterações críticas exigem permissão explícita e resultados verificáveis.'
)
HEX32 = re.compile(r'^[a-f0-9]{32}$')


def respond(brief, *, state_root=None, parent_id=None):
    if not isinstance(brief, str) or not 1 <= len(brief.strip()) <= 6000:
        raise ValueError('Mensagem deve conter de 1 a 6000 caracteres')
    root = Path(state_root) if state_root is not None else Path.home() / '.local' / 'share' / 'sagaz-zero' / 'projects'
    history = []
    if parent_id:
        if not isinstance(parent_id, str) or not HEX32.fullmatch(parent_id):
            raise ValueError('ID de conversa inválido')
        directory = root / parent_id
        file = directory / 'conversation.json'
        if directory.is_symlink() or file.is_symlink() or not file.is_file():
            raise ValueError('Histórico de conversa inválido')
        data = json.loads(file.read_text(encoding='utf-8'))
        history = data.get('messages', [])
        if not isinstance(history, list):
            raise ValueError('Histórico de conversa corrompido')
        for item in history:
            if not isinstance(item, dict) or item.get('role') not in ('user', 'assistant') or not isinstance(item.get('content'), str):
                raise ValueError('Histórico de conversa corrompido')
    messages = [{'role': 'system', 'content': SYSTEM}]
    messages.extend({'role': item['role'], 'content': item['content'][:3000]} for item in history[-12:])
    messages.append({'role': 'user', 'content': brief.strip()})
    response = Gateway(root).chat(LOCAL_UI, {'messages': messages, 'stream': False})
    choices = response.get('choices', [])
    content = choices[0].get('message', {}).get('content') if choices and isinstance(choices[0], dict) else None
    if not isinstance(content, str) or not content.strip():
        raise ValueError('O provedor não retornou resposta textual válida')
    conversation_id = uuid.uuid4().hex
    directory = root / conversation_id
    directory.mkdir(parents=True, exist_ok=False, mode=0o700)
    entry = {'id': conversation_id, 'parent_id': parent_id,
             'niche': 'general', 'method': 'llm_chat',
             'messages': (history + [{'role': 'user', 'content': brief.strip()},
                                     {'role': 'assistant', 'content': content.strip()}])[-40:]}
    file = directory / 'conversation.json'
    with file.open('x', encoding='utf-8') as output:
        output.write(json.dumps(entry, ensure_ascii=False, indent=2))
    file.chmod(0o600)
    return {'id': conversation_id, 'answer': content.strip(), 'mode': 'configured_model', 'status': 'text_generated'}
