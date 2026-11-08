# SagaZ ZeRo — Changelog

## 3.7.0-zeRo · HooLeeSh33t Edition by dSant — atualização 3 — 2026-11-08

Fase 6 do roadmap: desktop + sandbox de execução.

- `sagaz desktop [--port]` — abre a interface HooLeeSh33t Matrix como app (navegador);
  documentado o caminho Tauri/Electron para app nativo em `docs/DESKTOP.md`.
- **Sandbox em container** no agente: `sagaz agent ... --sandbox` roda `run_command`
  em `docker run --rm --network none --cap-drop ALL --security-opt no-new-privileges`,
  com a raiz montada e limites; se não houver Docker, **avisa e não executa**
  (nunca cai para execução sem isolamento). Imagem via `SAGAZ_SANDBOX_IMAGE`.
- `tests/test_agent.py`: +4 casos de sandbox (comando isolado, rede opt-in,
  escopo+confirmação, Docker ausente). Suíte total: 89 testes.


## 3.7.0-zeRo · HooLeeSh33t Edition by dSant — atualização 2 — 2026-11-08

Agente de código (estilo Claude Code), com GitHub e plugins — pacote `sagaz/agent/`.

### Agente
- `sagaz agent "<objetivo>"` — loop de agente por **tool-calling** OpenAI, rodando
  pelo Gateway auditado. Só-leitura por padrão; `--allow fs.write,exec,git.write`
  libera poderes; ações sensíveis **confirmam** (ou `--yes`).
- **Ferramentas**: `fs_list/read/search/stat/write/edit` (confinadas à raiz, backup),
  `run_command` (trava `is_destructive_command` + confirmação, timeout),
  `git_status/diff/branch/add/commit/push` (**sem force-push**; credenciais locais).
- **Escopos** `fs.read/fs.write/exec/git.read/git.write` com confirmação; nada é
  exposto na rede (a superfície web/MCP continua só-leitura).

### Plugins
- Plugins registram **ferramentas** via `plugins/<nome>/plugin.json`; cada tool só
  pede escopo declarado; carregam só quando **habilitados** (`sagaz plugin enable`).
- Exemplo em `plugins/example-wordcount/`. Docs em `docs/AGENT.md`.

### Testes
- `tests/test_agent.py` (23 casos): confinamento, escopos, confirmação, exec com
  trava, git sem force-push, registro, plugins e loop com modelo mockado.


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
