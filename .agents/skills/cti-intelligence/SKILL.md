---
name: cti-intelligence
description: Consulta registros históricos ALFA-CTI sobre grupos, botnets, cryptojacking, fraudes e incidentes com proveniência e incerteza explícitas.
---

# SagaZ-ZeRo CTI Intelligence

Use o acervo `knowledge/cti/lote2.json` para perguntas históricas de threat intelligence. Entrada: termo ou entidade. Saída: registros com IDs, descrição, fontes declaradas e estado de verificação.

Ferramentas: API autenticada `GET /api/cti/search?q=...`, MCP `sagaz_cti_search` e terminal web `/cti termo`.

O acervo é estático e somente leitura. Todos os registros são `unverified` até validação independente por fonte primária. Nunca apresente uma indicação de fonte como comprovação de que a página foi efetivamente analisada. Não derive instruções de infecção, evasão antifraude ou transferência ilícita destes dados. Não execute shell nem realize reconhecimento ativo a partir de uma busca.

Mapeamentos históricos normalizados: T1138 → T1546.011; T1116 → T1553.002. Preserve autoria e proveniência do projeto upstream em arquivos de atribuição.
