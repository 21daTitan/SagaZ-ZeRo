# SagaZ-ZeRo · HooLeeSh33t Edition _by dSant_ 🧢⚡

**Salve!** Isso aqui é a sua IA **do seu jeito** — multi-modelo, com a sua própria
chave (BYOK), rodando na sua máquina, no seu VPS ou até no Termux. Sem firula, sem
te prender: você manda, ela executa. Pega a visão? Então cola aí. 😎

> Edição derivada da obra-prima **Cassandra**, criada pelo mestre **Mörlsara**
> (_Morlsara Code Nexus_). A gente respeita a origem e põe a nossa manha por cima.
> Crédito de quem fez vem sempre junto — malandragem é com honra. 🙏

---

## O que esse bicho faz 🚀

- 🔑 **BYOK** — você pluga **sua** chave (OpenAI-compatible: OpenAI, Claude, Gemini, Ollama local, seu endpoint…). Nada de chave nossa, nada de conta pra criar.
- 🧠 **Multi-modelo** — troca de modelo na hora, sem drama.
- 🖥️ **Duas caras, a mesma alma:**
  - **HooLeeSh33t Matrix** (web) — a interface bonitona.
  - **Console Operador** (terminal/TUI) — pra quem curte o preto no branco.
- 🧩 **Skills** — memória de Discord (consentida e só-leitura), CTI, criativo dSant… e dá pra plugar mais.
- 🔒 **Na responsa** — chave guardada em arquivo `0600`, ação destrutiva **sempre** pede confirmação, nada exposto na internet sem você mandar.

---

## Bora rodar (3 passos e tá on) ▶️

```bash
# 1) checa se tá tudo nos trinques
python3 dsant.py doctor

# 2) abre o console operador (a melhor porta de entrada)
python3 -m sagaz operator
#    lá dentro: /conectar  → cola seu endpoint + modelo + chave (fica oculta)
#               /testar    → confirma que o modelo respondeu
#               aí é só digitar e conversar de verdade 💬

# 3) ou sobe a interface web HooLeeSh33t Matrix
python3 -m sagaz --web --port 8080
#    abre http://127.0.0.1:8080  (no VPS, use túnel SSH — não exponha a porta crua!)
```

Conectou o provedor? **O chat da web já fala com o modelo de verdade**, automático.
Sem provedor, o Core ainda prepara seu briefing localmente. Tá sempre fazendo algo. 👊

---

## Comandos que você vai usar 🎛️

| Comando | O que faz |
|---|---|
| `python3 -m sagaz operator` | Console operador (TUI) com chat real |
| `python3 -m sagaz --web` | Interface web HooLeeSh33t Matrix |
| `python3 -m sagaz god [deus\|devocional]` | Mostra/escolhe o perfil de autonomia |
| `python3 -m sagaz discord ingest msgs.json --consent` | Memória Discord (consentida, local) |
| `python3 -m sagaz doctor` | Diagnóstico rápido do núcleo |

Na interface, digite `/ajuda` pra ver tudo: `/cti`, `/skills`, `/status`, `/god`, `/discord`, `/criar`.

---

## Atualizar sem perder o seu edit 🔄

A Cassandra evolui lá na origem; a gente puxa as melhorias **sem apagar a sua manha**.
O passo a passo tá redondinho em **[`docs/UPSTREAM.md`](docs/UPSTREAM.md)** — porte
revisado, nada de merge na doida. O doutrinão completo da edição mora em
**[`docs/MASTER-PROMPT-SAGAZ.md`](docs/MASTER-PROMPT-SAGAZ.md)**.

---

## Na faixa da responsa ✋

Essa edição **não** embute ferramentas de evasão de filtro / anti-censura / exploração
ofensiva — e isso é escolha nossa, tá no [`NOTICE.md`](NOTICE.md). SagaZ-ZeRo é pra
construir, automatizar e criar na responsa. Antes de ligar bot de Discord, dá um
confere em [`docs/DISCORD_MEMORY.md`](docs/DISCORD_MEMORY.md) e
[`docs/GOD_MODE.md`](docs/GOD_MODE.md).

---

## Créditos 🫡

- **Edição:** SagaZ-ZeRo · HooLeeSh33t Edition — **by dSant** (`@21daTitan`, _Systemia Solutions_)
- **Obra original:** **Cassandra**, criada por **Mörlsara** — _Morlsara Code Nexus_
- **Upstream:** https://github.com/DarkyHArry/cassandra-agent

Tamo junto. Jaé! 🤝

---

```bash
python3 -m unittest discover -s tests -q   # roda a bateria de testes
```
