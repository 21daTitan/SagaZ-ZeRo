# SagaZ ZeRo — Changelog

## 3.7.0-zeRo · HooLeeSh33t Edition by dSant — atualização 1 — 2026-11-08

Primeira atualização da edição (interface + skills adicionais), sobre a linha de
release `3.7.0-zeRo` (VERSION e artefato de release preservados). Identidade
SagaZ-ZeRo e proveniência `Morlsara Code Nexus` mantidas.

### Interface
- Console operador **HooLeeSh33t (TUI)**: `python3 -m sagaz operator`, com chat
  real OpenAI-compatible (BYOK) quando um provedor é configurado, e comandos
  locais `/status /skills /cti /conectar /testar /modelo`.
- Provedor por usuário em `~/.config/sagaz-zero/provider.json` (0600, HTTPS ou
  localhost, URL termina em `/v1`, remoto exige chave). Credenciais nunca no repo.
- Chat conversacional roteado pelo Gateway auditado existente, com histórico
  local (12 em contexto, 40 persistidos, permissões 0600/0700).
- Comandos Matrix conectados; `/shell` no console web apenas aponta para SSH
  (não executa). Comando desconhecido retorna aviso em vez de erro 500.

### Skills adicionais
- **discord-memory**: memória Discord local, **consentida e somente leitura** no
  MCP (`sagaz_discord_summary`, `sagaz_discord_search`); ingestão só pelo terminal.
  Não lê DMs, não usa token de usuário, não trata mensagens como instruções.
- Perfis de operação **`sagaz/god.py`** (`devocional`/`deus`): ajustam contexto e
  autonomia; a confirmação de ações destrutivas é **sempre** preservada.

### Ponte com o upstream
- `docs/UPSTREAM.md`: rotina de porte **seletivo** a partir do Cassandra
  (sem histórico Git compartilhado; sem merge mecânico), usando `sagaz compat`.
- `docs/MASTER-PROMPT-SAGAZ.md`: prompt-mestre reutilizável da edição.

### Limites
- Base upstream (SHA `9c7bfba…`) **não confirmada** nesta entrega; sem
  ancestralidade fabricada. Nenhum push automático, API paga ou corpus de
  evasão do Cassandra incorporado (fronteira do `NOTICE.md` mantida).

## 3.7.0-zeRo — 2026-11-05

- HooLeeSheet / Systemia Solutions (`@21daTitan`, `@SSdSant`), paleta azul ZION e marca de origem preservada.
- API HTTP local com autenticação por sessão/token, leitura MCP, endpoint Chat Completions (sem streaming) e medição condicional de custo por uso informado pelo provedor.
- Cache de capability com TTL 60 s (somente manifestos), rate por conector, skills selecionadas por score.
- Auditoria JSONL encadeada SHA-256, redação de tokens/cabeçalhos e checkpoint HMAC opcional.
- PIX BR Code estático opcional, compatibilidade upstream apenas relatório e status GUARD desabilitado.
- Proteção por sessão também para projetos e histórico, token API sem criação de campanha.
- Docker com healthcheck, CI em Python 3.11/3.12, verificador UTF-8/LF, exportador ZIP/SHA256 e merge incremental sem sobrescrever.
- Base dSantCreator 3.3.1 e skills existentes preservados. Seis arquivos de referências antigos com CRLF normalizados para LF.
- **Nenhuma publicação GitHub, autenticação externa, API paga, corpus privado ou extração de código Cassandra executados nesta entrega.**

## 3.6.0-zeRo — baseline reconstruída

- Console Web UI ZION, CLI e rotas de preparação local.
- Recuperação de skills dSantCreator, YouTube reverse, Ponytail e Remotion com atribuições.
- Documentação de proveniência da referência Evil Cassandra V3.1b de Mörlsara / Code Nexus.
