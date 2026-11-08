# ROADMAP — SagaZ-ZeRo como Coding Agent (estilo Claude Code)

> Objetivo: transformar o **Console Operador** num **agente de código** que lê/edita
> arquivos, roda comandos **sob confirmação**, integra **GitHub** (branch, commit,
> push, PR) e aceita **plugins em geral** que registram novas ferramentas — sem
> abrir mão da segurança.

Documento de planejamento. Nada aqui executa sozinho; é o mapa do que construir.

> **Status (atualização 3):** Fases **1–6 implementadas**. Agente completo em
> `sagaz/agent/` (arquivo/exec/git, loop por tool-calling, escopos + confirmação,
> plugins). Fase 6: `sagaz desktop` (app) + **sandbox em container** no agente
> (`--sandbox`). Uso em [`docs/AGENT.md`](AGENT.md) e [`docs/DESKTOP.md`](DESKTOP.md).
> Evolução contínua fica por conta das próximas atualizações.

---

## 0. O que já joga a favor (não precisa reinventar)

| Peça existente | Para que serve no agente |
|---|---|
| `sagaz/tools/bus.py` + `tools/builtin.py` | **Barramento de ferramentas** — é onde cada nova tool é registrada |
| `sagaz/god.py` → `is_destructive_command()` | **Trava de confirmação** de ação perigosa (reaproveitar em tudo) |
| `sagaz/gateway/policy.py` (scopes) | **Permissões** — criar escopos novos (fs / exec / git) |
| `sagaz/gateway/audit.py` | **Auditoria** lacrada SHA-256 de cada ação |
| `sagaz/ai_session.py` + `operator_tui.py` | **Loop de conversa** onde o agente vai viver |
| `sagaz/connectors/*` + endpoint `/mcp` | Encaixe para **plugins MCP** externos |

---

## 1. Princípios de segurança (inquebráveis — valem para TODAS as fases)

- 🧱 **Confinamento**: ferramentas de arquivo só operam **dentro da raiz do projeto**; recusar `..`, caminhos absolutos e symlinks que escapem.
- ✋ **Confirmação**: **escrever, executar comando e push** sempre passam pela trava (`god.is_destructive_command` + confirmação explícita). Nada destrutivo silencioso.
- 🔑 **Credenciais fora do repo**: GitHub usa as credenciais locais do `git` do usuário, ou um token em arquivo `0600`/variável de ambiente — **nunca** commitado.
- 🔒 **Escopos separados**: `operator-fs` (arquivo) ≠ `operator-exec` (comando) ≠ `operator-git`. A **web/token-api fica só-leitura**; escrita/execução só no **console local**.
- 🧾 **Rastro**: toda ação de ferramenta entra na auditoria existente.
- 📦 **Isolamento real** para código não confiável: rodar dentro de container/sandbox é recomendado (ver Fase 6).

---

## 2. Fase 1 — Ferramentas de arquivo (fundação)

Novas tools no barramento (escopo `operator-fs`):
- `fs_list(path)`, `fs_read(path)`, `fs_search(regex)`, `fs_stat(path)` — **só-leitura**, confinadas à raiz.
- `fs_write(path, content)` e `fs_edit(path, old, new)` — **exigem confirmação**; gravam **backup** em `state/backups/` antes de alterar (como o `apply.py` do Operator V4 já faz).

**Testes (obrigatórios):** path traversal bloqueado, symlink recusado, confirmação exigida, backup criado.

---

## 3. Fase 2 — Execução de comandos sob trava

- `run_command(cmd)` (escopo `operator-exec`, **só console local**):
  - passa por `is_destructive_command()` → se perigoso, **confirma**;
  - `timeout` obrigatório, captura `stdout`/`stderr`, **nunca** `sudo` automático;
  - registra na auditoria.

**Testes:** comando destrutivo pede confirmação; timeout corta; saída capturada.

---

## 4. Fase 3 — Loop de agente (o "cérebro")

- Um laço: **objetivo → o modelo propõe um plano + chamadas de ferramenta (tool-use) → executa → lê o resultado → itera**, respeitando `max_iterations` do perfil `god` (devocional = curto, deus = longo).
- Roda **pelo Gateway** (ganha auditoria + medição de custo de graça).
- Guarda o **transcript** local (como `ai_session` já faz).
- Regra de ouro: o modelo **propõe**, a trava/escopo **decide** o que pode rodar.

---

## 5. Fase 4 — Integração GitHub

Tools (escopo `operator-git`), embrulhando o **git local** do usuário:
- `git_status`, `git_branch`, `git_commit`, `git_pull`, `git_push`.
- `github_pr` (opcional): via **API do GitHub** com **token do usuário** (arquivo `0600`/env), para abrir PR e ler status de CI.

**Regras fixas:** nunca `force-push`; sempre **branch de trabalho**; **push confirma**; **PR só quando o usuário pede**; token com escopo mínimo.

**Testes:** push exige confirmação; force-push bloqueado; token nunca aparece em log.

---

## 6. Fase 5 — Plugins em geral

Hoje existem **skills** (`.agents/skills/`, conhecimento). Estender para **plugins que registram FERRAMENTAS**:

- **Manifesto** por plugin (`plugin.toml`/`json`): `nome`, `versão`, `ferramentas` que expõe, **escopos/permissões** que pede, comandos.
- **Carregador** que: valida o manifesto, **mostra ao usuário o que o plugin quer tocar** (arquivo? shell? git? rede?), só registra no `tools/bus` o que for **aprovado**.
- **Isolamento por escopo**: sem permissão concedida, o plugin **não roda** aquela ferramenta.
- **Hooks** (antes/depois de ferramenta) — opcional, para logging/políticas.
- **Compat MCP**: um plugin pode ser um **servidor MCP externo** que o SagaZ pluga (os `connectors/` já são o encaixe disso).
- **CLI**: `sagaz plugin list | install | enable | disable`.

**Testes:** plugin sem permissão não executa; manifesto inválido é recusado; aprovação é explícita.

---

## 7. Fase 6 — Empacotar como desktop (opcional)

- **Tauri** ou **Electron** embrulhando a interface web, **ou** distribuir o TUI + instalador (já há launchers e o fluxo Termux).
- Para rodar código não confiável com segurança: **container** (Docker) como sandbox de execução — o repo já tem `Dockerfile`/`docker-compose.yml` de base.

---

## 8. Sequência sugerida (do mais seguro ao mais poderoso)

1. **Fase 1** (arquivo read-only) → já dá um "leitor de código" útil e sem risco.
2. **Fase 1 (escrita)** + **Fase 2** (exec) com a trava → vira editor/executor.
3. **Fase 3** (loop) → vira **agente** de verdade.
4. **Fase 4** (GitHub) → fecha o fluxo dev (branch→commit→push→PR).
5. **Fase 5** (plugins) → abre pra comunidade estender.
6. **Fase 6** (desktop/sandbox) → produto.

---

## 9. Limites honestos

- Executar código é sério: para código de terceiros, **sandbox em container** não é luxo, é necessidade.
- GitHub via API precisa do **token do usuário**, com escopo mínimo e fora do repo.
- A **licença** da edição (para uso comercial) continua pendente — ver [`NOTICE.md`](../NOTICE.md). Resolver antes de distribuir plugins/serviço pago.
- Este roadmap **reduz** o caminho; não promete que cada fase sai sem ajuste.
