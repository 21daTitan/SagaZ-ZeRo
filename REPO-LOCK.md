# 🔒 REPO-LOCK — Regras de preservação do SagaZ-ZeRo

**Commit de referência (estado travado):** `72920f2`
**Repositório:** https://github.com/21daTitan/SagaZ-ZeRo
**Vigente a partir de:** HooLeeSh33t v0.1

---

## O que significa "travado" aqui

A partir do commit `72920f2`, os arquivos e pastas listados abaixo são
considerados **resolvidos**. Qualquer trabalho novo no projeto deve ser
**aditivo** — arquivos novos, módulos novos, documentos novos — e não deve
editar, apagar, truncar ou limitar o conteúdo já existente nesses caminhos,
salvo autorização explícita e pontual do dSanT.

## Arquivos e pastas travados (estado em `72920f2`)

```
agent.py
web_ui.py
cassandra/                  (client.py, providers.py, filter.py, compact.py,
                              environment.py, toolfetch.py, crypto.py, guard.py,
                              attribution.py ← NUNCA alterar, créditos do autor original)
cassandra-skill/            (655+ arquivos de skill)
sagaz_zero/__init__.py      (alias de compatibilidade original)
sagaz-zero.sh
sagaz-zero.bat
sagaz-zero.ps1
cassandra.sh / .bat / .ps1  (launchers originais preservados)
README.md                   (conteúdo até o apêndice "HooLeeSh33t v0.1";
                              novos apêndices no FINAL do arquivo são permitidos,
                              reescrever o que já existe não é)
README.pt-br.md
README.zh-cn.md
NOTICE-SAGAZ.md
.env.example
requirements.txt
.gitignore
model.png
LICENSE (se existir)
```

## Regras não-negociáveis (consolidado das diretrizes originais do projeto)

1. **Não publicar credenciais, tokens, sessões ou `.env` com segredos.**
2. **Não pedir tokens no chat.**
3. **Não alterar o ZIP original** da entrega-base (Cassandra v3.1).
4. **Não apagar repositório, histórico ou tags.**
5. **Não usar `push --force`.**
6. **Substituição remota exige backup remoto confirmado antes** (branches `backup/*`).
7. **Não alterar `cassandra/attribution.py`** — créditos do autor original (Mörlsara).
8. **Não inventar licença geral ausente.**
9. **Não apresentar esta edição como publicação oficial do autor original.**
10. **Destino autorizado único:** `https://github.com/21daTitan/SagaZ-ZeRo`

## Como adicionar funcionalidade nova a partir de agora

✅ **Permitido:**
- Criar arquivos novos (módulos, scripts, documentos)
- Criar novos comandos/launchers que chamem o que já existe sem modificá-lo
- Apêndices no FINAL de documentos existentes (nunca reescrever o meio/início)
- Novas versões documentadas (ex: `HOOLEESH33T-v0.2.md`, `v0.3.md`, ...), cada
  uma travando o estado anterior e documentando só o que mudou

❌ **Não permitido sem autorização explícita do dSanT:**
- Editar `agent.py`, `web_ui.py` ou qualquer arquivo em `cassandra/`
- Remover ou truncar qualquer skill em `cassandra-skill/`
- Reescrever README.md, NOTICE-SAGAZ.md ou qualquer doc já publicado
- Qualquer operação destrutiva no Git (force push, apagar branch/tag, reset remoto sem backup)

---

## Exceções autorizadas (edições pontuais em arquivo travado)

| Data | Arquivo | O que mudou | Autorizado por |
|---|---|---|---|
| 2026-11-09 | `web_ui.py` | Endpoint `GET /api/history` (expõe a `conversation` global já existente) + JS que redesenha o chat ao carregar a página | dSanT, pedido direto no chat — "quero que a memória fique pra quando eu voltar" |
| 2026-11-09 | `web_ui.py` | Conserto da interface Web (só dentro de `HTML_CONTENT`, nenhuma rota de backend tocada): provider/modelo paravam de virar `[object Object]`, status de shell/cifrado/sanitizado/anti-recusa paravam de nunca atualizar, credenciais paravam de poder forçar provider/base_url/modelo | dSanT, pedido direto no chat — "a interface tá uma merda... corrija e atualize a interface" |
| 2026-11-09 | `web_ui.py` | `#app` tinha `grid-template-rows: auto 1fr auto` (3 linhas) pra 4 filhos (header/provider-bar/chat-area/input-area) — o `1fr` caía na provider-bar e esticava ela (vazia) quase até a tela inteira, criando o buraco preto gigante. Corrigido pra `auto auto 1fr auto` | dSanT, print mostrando o buraco preto gigante mesmo após o conserto anterior |
| 2026-11-09 | `web_ui.py` | Chuva Matrix de fundo usava `shadowBlur` por glifo/coluna/frame (~22 FPS) — operação cara de Canvas 2D, travava o celular. Removido o blur, agrupada a troca de fonte, frame rate reduzido | dSanT — "ta travando muito tambem" |
| 2026-11-09 | `web_ui.py` | Buraco preto persistiu em Chrome Android real mesmo com o grid corrigido (confirmado: aba nova, commit certo, serviço saudável). `#app` trocou de CSS Grid pra flexbox de coluna simples (`flex:0 0 auto` nos 3 filhos fixos, `flex:1 1 auto; min-height:0` no `#chat-area`) — layout mais robusto e previsível entre navegadores | dSanT — "vai tomar no cu" (buraco continuava mesmo em aba nova confirmada) |
| 2026-11-09 | `web_ui.py` | Header sumia depois de um tempo de uso (não no load) — era a página rolando sozinha (rubber-band scroll por toque, `overflow:hidden` não trava isso 100% em mobile). `html,body` ganharam `position:fixed`+`overscroll-behavior:none`; `#chat-area`/`#user-input` ganharam `overscroll-behavior:contain` | dSanT — "ficou um tempinho e sumiu o painel de cima dnv" |
| 2026-11-09 | `web_ui.py` | Chat nunca respondia: `/api/chat` sempre foi `StreamingResponse(media_type="text/plain")` (markdown puro, sem envelope), mas o JS esperava formato SSE/JSON estilo OpenAI (`data: {...}` com `delta.content`) — nunca bateu, bolha ficava vazia sem erro. Parser trocado pra só decodificar e acrescentar o texto puro, igual o servidor sempre mandou | dSanT — "Nao mw responde mas ta conectado" |

---

## Histórico de versões travadas

| Versão | Commit | Data | O que mudou |
|---|---|---|---|
| Base (rebrand inicial) | `72920f2` | 2026-11-09 | Cassandra → SagaZ-ZeRo (nomes, cores, interface Matrix) |
| HooLeeSh33t v0.1 | `6c1d652` | 2026-11-09 | Personas SagaZ/ZeRo, instaladores desktop, guia Android, esta trava |
| HooLeeSh33t v0.2 | `3f08055` | 2026-11-09 | `deploy-vps.sh`: deploy permanente em VPS (systemd + proxy autenticado) |
| HooLeeSh33t v0.3 | `e562dde` | 2026-11-09 | Acesso sem senha (opt-in pra religar), histórico visível ao voltar (exceção autorizada em `web_ui.py`) |
| HooLeeSh33t v0.4 | `4bb27ed` | 2026-11-09 | Conserto da interface Web: provider/modelo, status, shell e "forçar API" (exceção autorizada em `web_ui.py`, só na `HTML_CONTENT`) |

---

Ordem e Progresso. Quem mexer, documenta. Quem documentar, não quebra o que já tava rodando.
