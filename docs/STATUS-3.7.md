# SagaZ ZeRo 3.7 — estado verificado e pendências

## Identidade

Operador: HooLeeSheet. Autor do produto: dSant / Systemia Solutions (`@21daTitan`, `@SSdSant`). Referência upstream: Evil Cassandra V3.1b de Mörlsara (`@DarkyHArry`) / Code Nexus, https://github.com/DarkyHArry/cassandra-agent. Marca fixa `Morlsara Code Nexus`.

Os arquivos dSantCreator 3.3.1 foram usados para recuperar o console e o sistema de campanhas. **Não há código Cassandra nesta distribuição, nem espelhamento de seu repositório.** Não atribuir funções de Cassandra ao SagaZ sem implementá-las e testá-las.

## Backlog B-01 a B-15

| Item | Estado nesta entrega | Critério |
|---|---|---|
| B-01 Capability TTL 60 s | Parcial | cache de manifesto e isolamento de conector; negociação remota pendente |
| B-02 Rate por conector | Implementado | `RateLimiter`; chamadas autenticadas por identidade |
| B-03 Ledger e checkpoint | Parcial | hash-chain, verificação e HMAC; compactação e assinatura de arquivo externo pendentes |
| B-04 Skill por score, máximo 1 | Implementado | regras determinísticas, sem chamada a LLM |
| B-05 OpenAPI → MCP | Pendente | nenhuma ponte genérica instalada |
| B-06 Custo real e corte 80% | Parcial | uso reportado pelo endpoint e preço explícito; não mede rota legada `DSANT_*` |
| B-07 Redação de segredo | Implementado | campos/header/query nomeados, bearer patterns; segredos arbitrários exigem validação |
| B-08 Compat auto-apply | Pendente | relatório somente, não aplica sem autorização |
| B-09 GUARD janela/microfone | Não incluído | nenhum serviço furtivo ou monitoramento de microfone |
| B-10 Healthcheck Docker | Implementado | HTTP `/healthz`, porta localhost no host Docker Compose |
| B-11 CI Python 3.11/3.12 | Implementado | matrix, unit tests e auditoria estrita de bytes |
| B-12 Release cosign/CycloneDX | Pendente | ZIP com SHA256, sem assinatura criptográfica externa |
| B-13 MCP resources/prompts | Parcial | métodos de lista/leitura/get por JSON-RPC HTTP, não transportes completos |
| B-14 `/gateway/cost` | Implementado | lista recente e agregado por conector na camada Python |
| B-15 PIX tiers | Pendente | BR Code estático com chave real opcional; sem rotação por tiers |

## Interfaces e permissões

- Interface ZION: Web UI com painel local, animação reduzida para preferências `prefers-reduced-motion` e CSS azul.
- `/healthz` e `/api/attribution` são públicos no servidor local.
- `/api/projects`, `/api/context/*`, `/api/conversation/*`, `/api/sources` e `/api/integrations` exigem sessão UI.
- `/mcp` e `/v1/chat/completions` exigem sessão UI ou token API. `X-Connector` não muda escopo.
- Ferramentas MCP são read-only. Não há `shell`, `fs_write` ou execução implícita.
- Preços e utilização de tokens dos provedores reais não foram confirmados externamente.

## Pendências de entrada

- Chave PIX real se quiser ativar BR Code. Não publicar nem incluir no ZIP.
- URLs de vídeos `AWbpxJPzltc` e `hEBmmSCZODg`: aguardar evidência verificável para mapear conteúdo.
- API real, serviços e licenças de terceiros dependem da configuração do operador.
- Estado remoto do GitHub `21daTitan/SagaZ-ZeRo` **não inspecionado** nesta sessão; nenhuma publicação foi feita.
