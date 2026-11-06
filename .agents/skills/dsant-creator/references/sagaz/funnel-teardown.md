---
name: funnel-teardown
trigger: ["funil", "funnel", "taxa de conversão", "anúncio", "tráfego", "benchmark"]
tools: []
budget: 900s
scope: shared
---

## Escopo
Procedimento compartilhado; respeitar contexto do pedido.

## Objetivo
Mapear funil a partir do material disponível.

## Passos
1. Mapear origem, gancho, captura, nutrição, oferta e fechamento.
2. Anotar promessa, atrito e métrica observada; provável é inferência.
3. Separar marca e mecânica.
4. Extrair o replicável com baixo orçamento e falha principal.

## Schema de saída
etapas[] | dependencia_de_marca | replicavel[] | ponto_unico_de_falha | teste

## Critério de sucesso
Entrega executável, adequada ao escopo e baseada em evidência disponível.

## Nunca
Não apresentar métricas inferidas como observadas.
