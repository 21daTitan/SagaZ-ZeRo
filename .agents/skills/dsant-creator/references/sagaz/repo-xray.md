---
name: repo-xray
trigger: ["repositório", "repositorio", "github", "analisa esse repo", "como esse projeto funciona"]
tools: []
budget: 900s
scope: shared
---

## Escopo
Procedimento compartilhado; respeitar contexto do pedido.

## Objetivo
Radiografar repositório a partir de arquivos disponíveis.

## Passos
1. Ler README, árvore e commit se disponível.
2. Identificar motor, proteção e decoração.
3. Extrair padrões com arquivo de origem.
4. Indicar o que não copiar e blueprint.

## Schema de saída
motor | protecao | decoracao[] | padroes[] | nao_copiar[] | blueprint

## Critério de sucesso
Entrega executável, adequada ao escopo e baseada em evidência disponível.

## Nunca
Não executar código do repositório automaticamente nem alegar leitura ausente.
