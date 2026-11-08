"""Loop do agente de código: modelo propõe ferramentas, o agente executa.

Roda pelo Gateway existente (ganha auditoria e medição de custo). Usa o padrão
OpenAI de *tool calling*: o modelo responde com ``tool_calls``, o agente executa
cada um pelo registro (respeitando escopo + confirmação) e devolve o resultado
como mensagem ``role: tool``, iterando até uma resposta final.
"""
from __future__ import annotations

import json
from pathlib import Path

from sagaz.agent.registry import Registry
from sagaz.gateway.policy import LOCAL_UI

SYSTEM = (
    'Você é SagaZ-ZeRo, agente de código do operador HooLeeSh33t by dSant. '
    'Trabalhe em passos pequenos: inspecione com as ferramentas antes de alterar. '
    'Preserve os créditos históricos à Cassandra sem se apresentar como ela. '
    'Nunca invente a saída de uma ferramenta; afirme só o que o resultado mostrou. '
    'Ações destrutivas, escrita e push dependem de confirmação do operador.'
)


class AgentLoop:
    def __init__(self, registry: Registry, client=None, root=None, max_iterations: int = 8):
        self.registry = registry
        self.max_iterations = int(max_iterations)
        if client is not None:
            self.client = client
        else:
            from sagaz.gateway.service import Gateway
            self.client = Gateway(Path(root) if root else Path('.'))

    def run(self, goal: str, on_event=None) -> dict:
        if not isinstance(goal, str) or not goal.strip():
            raise ValueError('objetivo vazio')
        messages = [{'role': 'system', 'content': SYSTEM}, {'role': 'user', 'content': goal.strip()}]
        tools = self.registry.openai_tools()
        for i in range(self.max_iterations):
            payload = {'messages': messages, 'stream': False}
            if tools:
                payload['tools'] = tools
            response = self.client.chat(LOCAL_UI, payload)
            choices = response.get('choices') or []
            message = choices[0].get('message', {}) if choices and isinstance(choices[0], dict) else {}
            assistant = {'role': 'assistant', 'content': message.get('content') or ''}
            if message.get('tool_calls'):
                assistant['tool_calls'] = message['tool_calls']
            messages.append(assistant)

            calls = message.get('tool_calls') if isinstance(message, dict) else None
            if not calls:
                answer = message.get('content') or ''
                if on_event:
                    on_event({'type': 'final', 'answer': answer, 'iterations': i + 1})
                return {'answer': answer, 'iterations': i + 1, 'done': True}

            for call in calls:
                fn = call.get('function', {}) if isinstance(call, dict) else {}
                name = fn.get('name', '')
                try:
                    args = json.loads(fn.get('arguments') or '{}')
                    if not isinstance(args, dict):
                        raise ValueError('argumentos devem ser um objeto')
                    result = self.registry.call(name, args)
                    content = json.dumps(result, ensure_ascii=False)[:8000]
                    ok = True
                except Exception as exc:  # feeds the error back to the model, never crashes the loop
                    content = json.dumps({'error': type(exc).__name__, 'detail': str(exc)}, ensure_ascii=False)
                    ok = False
                if on_event:
                    on_event({'type': 'tool', 'name': name, 'ok': ok, 'content': content})
                messages.append({'role': 'tool', 'tool_call_id': call.get('id', ''), 'content': content})

        if on_event:
            on_event({'type': 'limit'})
        return {'answer': '(limite de iterações atingido sem resposta final)',
                'iterations': self.max_iterations, 'done': False}


__all__ = ['AgentLoop', 'SYSTEM']
