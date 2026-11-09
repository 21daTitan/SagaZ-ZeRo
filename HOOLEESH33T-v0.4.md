# ⬡⬢ HooLeeSh33t v0.4 — Conserto da interface Web

**Status:** Lançado
**Base travada:** commit da v0.3 (ver [`REPO-LOCK.md`](REPO-LOCK.md))
**Regra:** uma edição em arquivo travado nesta versão, **explicitamente
autorizada pelo dSanT** no chat, registrada na tabela de exceções do
`REPO-LOCK.md`.

---

## Por que essa versão existe

A versão web tava feia e quebrada de verdade: provider e modelo
mostrando `[object Object]` repetido, layout torto, e funcionalidade
que existia na Cassandra original (forçar provider/base_url/modelo,
badges de status) tinha ficado pelo caminho na reescrita visual
Matrix cyan. Reportado direto: *"a interface tá uma merda... fiquei
até triste"*. Com razão — essa versão conserta os bugs reais, não só
o sintoma.

## O que estava quebrado, de fato (causa raiz)

1. **`[object Object]` no PROVIDER e no MODELO.**
   `provider_catalog()` (em `cassandra/providers.py`, núcleo
   preservado) devolve uma **lista de objetos**
   (`{key, label, base_url, default_model, models, ...}`) — nunca
   devolveu strings. O JS da reescrita anterior assumia string pura
   (`new Option(p, p)`), e todo objeto virava a string literal
   `"[object Object]"` ao ser colocado num `<option>`. Isso também
   explica os ~10 itens duplicados no seletor nativo do Android: eram
   os ~10 provedores do catálogo, todos estourando pro mesmo texto
   inútil.

2. **Dropdown de modelo ficava vazio sem motivo aparente.**
   `/api/models` (que consulta `GET /v1/models` de verdade na conta)
   **ignora qualquer parâmetro de provider na URL** — ele só responde
   pela credencial ativa no momento. A reescrita anterior chamava
   esse endpoint toda vez que o PROVIDER mudava, mesmo sem nenhuma
   credencial configurada ainda, e sempre voltava vazio. O catálogo
   local (que já tem a lista de modelos de cada provider, estática)
   nunca era usado pra popular a tela — só pra decorar o resultado da
   API depois.

3. **Toggle de SHELL e os badges de status nunca atualizavam.**
   O servidor sempre devolveu o campo `allow_shell` (em
   `/api/shell/toggle` e `/api/status`). O JS da reescrita anterior
   lia um campo chamado `shell_enabled`, que **nunca existiu** — então
   todo resultado vinha `undefined`, e nada na tela refletia o estado
   real. Pelo mesmo motivo, os badges de cifrado/sanitizado/
   anti-recusa que existiam na Cassandra original simplesmente
   desapareceram: a tela nunca lia os campos `encrypt`/`sanitize`/
   `guard` que `/api/status` sempre devolveu.

4. **"Forçar API" não existia de verdade.**
   O botão de salvar credenciais mandava `base_url: null` quando o
   campo ficava vazio (o backend espera string, não `null`) e nunca
   mandava `model` nenhum — ou seja, não tinha como forçar um modelo
   específico via essa tela, só a chave e (as vezes) o provider.

## O que mudou (só dentro de `HTML_CONTENT`, em `web_ui.py`)

- PROVIDER e MODELO agora usam `p.key`/`p.label` corretamente — sem
  stringificar objeto.
- Seletor de MODELO é populado a partir do **catálogo local**
  (sempre disponível, mesmo sem credencial) e depois **enriquecido**
  com a lista real da conta (`/api/models`) quando já existe
  credencial ativa — sem nunca ficar vazio à toa.
- Campo novo **"forçar modelo"** na barra: digitou ali, esse valor
  passa por cima da seleção do dropdown ao enviar mensagem.
- Modal **⚙ CONFIGURAR API** ganhou campo de **MODELO** (além de
  provider e base URL) — agora dá pra forçar os três: provider,
  endpoint e modelo, igual a Cassandra original permitia.
- Toggle de SHELL e badges de status (**PROVIDER ativo + nº de
  credenciais, cifrado, sanitizado, anti-recusa**) lêem os campos
  reais que o servidor sempre devolveu (`allow_shell`, `encrypt`,
  `sanitize`, `guard`, `provider_label`, `credentials`) — voltam a
  bater com a realidade.
- Barra reorganizada em duas linhas (seletores / badges) pra não
  espremer tudo numa linha só no mobile.
- Botões renomeados pra bater com a nomenclatura da Cassandra
  original: **"LIMPAR SESSÃO"** e **"SALVAR / FORÇAR API"**.

**Nenhuma rota de backend foi tocada** — `/api/providers`,
`/api/models`, `/api/status`, `/api/shell/toggle`, `/api/credentials`,
`/api/clear`, `/api/chat` continuam exatamente como estavam. O
problema inteiro era de leitura/escrita incorreta desses dados no
front-end que eu tinha reescrito do zero sem conferir o formato real
contra o backend e contra a interface original — essa versão corrige
isso.

## Correção adicional: o buraco preto gigante (bug de grid CSS)

Depois do conserto acima, ainda sobrou o maior sintoma visual: um
buraco preto enorme entre a barra de provider/modelo e as mensagens.
Causa raiz, confirmada renderizando a página localmente (Playwright,
viewport mobile) e inspecionando o layout:

`#app` é um CSS grid com `grid-template-rows: auto 1fr auto` — **3
linhas** — só que tem **4 filhos diretos**: `header`, `#provider-bar`,
`#chat-area`, `#input-area`. O grid casa as linhas explícitas na
ordem do DOM, então o `1fr` (que devia esticar o `#chat-area`) caía
em cima do `#provider-bar`, esticando ele — vazio — até quase a tela
inteira, e empurrando o chat pra uma faixinha minúscula no fim. O
`#chat-area` caiu numa linha implícita de tamanho automático. Esse
bug **já existia antes** da reescrita Matrix cyan; só ficou
gigantesco agora porque a barra de badges/pills do conserto acima
ocupa mais espaço de conteúdo, mas o buraco em si sempre foi esse
grid mal dimensionado, não os pills.

**Fix:** `grid-template-rows: auto auto 1fr auto` — 4 linhas pros 4
filhos, `1fr` agora cai certinho no `#chat-area`.

## Correção adicional: travamento/lag na animação de fundo

Depois do grid resolvido, sobrou reclamação de travamento geral na
página no celular. Causa: a chuva Matrix no fundo (`<canvas>`) usava
`ctx.shadowBlur` em **cada glifo, de cada coluna, a cada frame**
(~22 FPS) — `shadowBlur` é uma das operações mais caras que existem
em Canvas 2D, principalmente em GPUs de celular, e aqui rodava até
mais de mil vezes por segundo sem parar, pra sempre, enquanto a
página ficasse aberta.

**Fix:** removido o `shadowBlur` por completo (o brilho da "cabeça"
da chuva agora é só uma cor mais clara, sem blur), a troca de fonte
foi agrupada (era 2x por coluna por frame, virou 2x por frame
inteiro), e o ritmo caiu de 45ms pra 60ms por frame. Efeito visual
continua o mesmo (chuva Matrix com cabeça clara e trilha escura),
só sem o custo de GPU que tava travando a interface.

## Correção adicional: buraco preto persistiu mesmo com o grid corrigido

O conserto do `grid-template-rows` ajudou, mas em Chrome Android real
(não reproduzido no teste headless anterior) o buraco preto continuou
aparecendo — inclusive sem header/barra visíveis, num teste numa aba
nova de verdade (confirmado: 1 aba só, commit certo rodando, serviço
saudável). Em vez de continuar caçando a causa exata via print de
celular, troquei a abordagem inteira: **`#app` deixou de ser CSS
Grid e virou flexbox de coluna simples**.

Cada filho direto (`header`, `#provider-bar`, `#chat-area`,
`#input-area`) agora usa `flex: 0 0 auto` (ocupa só a altura do
próprio conteúdo) — exceto `#chat-area`, que usa
`flex: 1 1 auto; min-height: 0` (pega o espaço que sobra; o
`min-height: 0` é obrigatório, senão um item flex não encolhe abaixo
do tamanho do próprio conteúdo e o `overflow-y: auto` dele simplesmente
não funciona). Flexbox-de-coluna-com-um-item-crescendo é o padrão de
layout mais testado e previsível que existe pra isso — bem menos
propenso a bug de dimensionamento entre navegadores do que Grid com
linhas explícitas.

Validado com Playwright emulando Pixel 7 Android (viewport, user
agent e device scale factor reais): header 47px, barra 134px, chat
549px, input 110px — proporções corretas. O espaço vazio que sobra
no meio é esperado (chat novo, sem credencial, sem mensagem) — não é
mais bug de layout quebrado.

---

## O que NÃO foi tocado além do registrado

Tudo mais continua como estava. Só a `HTML_CONTENT` dentro de
`web_ui.py`, pelos motivos acima.

---

Ordem e Progresso. 🤙
