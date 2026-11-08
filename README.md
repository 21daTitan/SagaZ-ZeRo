# SagaZ-ZeRo · HooLeeSh33t Edition _by dSant_ 🧢⚡

**Salve!** Isso aqui é a sua IA **do seu jeito** — multi-modelo, com a sua própria
chave (BYOK), rodando na sua máquina, no seu VPS ou até no Termux. Sem firula, sem
te prender: você manda, ela executa. Pega a visão? Então cola aí. 😎

> Edição derivada da obra-prima **Cassandra**, criada pelo mestre **Mörlsara**
> (_Morlsara Code Nexus_). A gente respeita a origem e põe a nossa manha por cima.
> Crédito de quem fez vem sempre junto — malandragem é com honra. 🙏
>
> 🇬🇧 English version: [`README.en.md`](README.en.md)

---

## O que esse bicho faz 🚀

- 🔑 **BYOK** — você pluga **sua** chave (OpenAI-compatible: OpenAI, Claude, Gemini, Ollama local, seu endpoint…). Nada de chave nossa, nada de conta pra criar.
- 🧠 **Multi-modelo** — troca de modelo na hora, sem drama.
- 🖥️ **Duas caras, a mesma alma:** **HooLeeSh33t Matrix** (web) e o **Console Operador** (terminal/TUI).
- 🤖 **Agente de código** — `sagaz agent` no estilo Claude Code: lê/edita arquivos, roda comando e mexe no Git **sob permissão e confirmação**. Veja [`docs/AGENT.md`](docs/AGENT.md).
- 🧩 **Skills + Plugins** — memória de Discord (consentida e só-leitura), CTI, criativo dSant… e **plugins** que registram novas ferramentas.
- 🔒 **Na responsa** — chave guardada em arquivo `0600`, ação destrutiva **sempre** pede confirmação, nada exposto na internet sem você mandar.
- 🪶 **Leve que só** — o núcleo roda **só com Python padrão**. Zero `pip` obrigatório.

---

## 📦 Instalação — em qualquer terminal, qualquer sistema

**Só precisa de 2 coisas:** `git` + `Python 3.10 ou mais novo`. O resto o próprio
projeto já traz. Escolhe o seu sistema abaixo e cola os comandos:

### 🐧 Linux
```bash
# Debian / Ubuntu / Mint / Pop!_OS
sudo apt update && sudo apt install -y git python3
# Fedora:   sudo dnf install -y git python3
# Arch:     sudo pacman -S --needed git python

git clone https://github.com/21daTitan/SagaZ-ZeRo.git
cd SagaZ-ZeRo
python3 -m sagaz operator
```

### 🍎 macOS
```bash
# Precisa do Homebrew (brew.sh). Depois:
brew install git python
git clone https://github.com/21daTitan/SagaZ-ZeRo.git
cd SagaZ-ZeRo
python3 -m sagaz operator
```

### 🪟 Windows (PowerShell)
```powershell
winget install Git.Git Python.Python.3.12
# feche e reabra o PowerShell depois de instalar
git clone https://github.com/21daTitan/SagaZ-ZeRo.git
cd SagaZ-ZeRo
python -m sagaz operator       # no Windows é "python", sem o 3
```

### 📱 Android (Termux)
```bash
pkg update && pkg install -y git python
git clone https://github.com/21daTitan/SagaZ-ZeRo.git
cd SagaZ-ZeRo
python -m sagaz operator
```

> **Importante:** rode sempre de **dentro** da pasta `SagaZ-ZeRo` (é de lá que o
> `python -m sagaz` acha o projeto).
>
> **Quer um comando global `sagaz`?** (opcional) `pip install -e .` dentro da pasta.
>
> **Skills de mídia** (voz, vídeo, legenda) são **opcionais**:
> `pip install -r requirements-media.txt`.

---

## ▶️ Primeira vez: conectar e conversar

```bash
python3 -m sagaz doctor        # 1) checa se tá tudo nos trinques
python3 -m sagaz operator      # 2) abre o console operador
#   lá dentro:
#     /conectar  → cola seu endpoint (/v1), modelo e a chave (fica oculta)
#     /testar    → confirma que o modelo respondeu
#     aí é só digitar e conversar de verdade 💬
```

Quer a interface web bonitona?
```bash
python3 -m sagaz --web --port 8080
#   abre http://127.0.0.1:8080  (no VPS, use túnel SSH — não exponha a porta crua!)
```
Conectou o provedor? **O chat da web já fala com o modelo de verdade**, automático.
Sem provedor, o Core ainda prepara seu briefing localmente. Tá sempre fazendo algo. 👊

---

## 🎛️ Comandos que você vai usar

| Comando | O que faz |
|---|---|
| `python3 -m sagaz operator` | Console operador (TUI) com chat real |
| `python3 -m sagaz --web` | Interface web HooLeeSh33t Matrix |
| `python3 -m sagaz agent "<objetivo>"` | Agente de código (lê/edita/roda/git sob permissão) |
| `python3 -m sagaz plugin list` | Lista plugins instalados |
| `python3 -m sagaz desktop` | Abre a HooLeeSh33t Matrix como app |
| `python3 -m sagaz agent "<obj>" --sandbox` | Agente rodando comando em container isolado |
| `python3 -m sagaz god [deus\|devocional]` | Mostra/escolhe o perfil de autonomia |
| `python3 -m sagaz discord ingest msgs.json --consent` | Memória Discord (consentida, local) |
| `python3 -m sagaz doctor` | Diagnóstico rápido do núcleo |

Na interface, digite `/ajuda` pra ver tudo: `/cti`, `/skills`, `/status`, `/god`, `/discord`, `/criar`.

---

## 🔄 Atualizar sem perder o seu edit

A Cassandra evolui lá na origem; a gente puxa as melhorias **sem apagar a sua manha**.
Passo a passo em **[`docs/UPSTREAM.md`](docs/UPSTREAM.md)** (porte revisado, nada de
merge na doida). Doutrinão completo em **[`docs/MASTER-PROMPT-SAGAZ.md`](docs/MASTER-PROMPT-SAGAZ.md)**.

Já tem o projeto clonado e quer só a versão nova?
```bash
cd SagaZ-ZeRo
git pull
```

---

## ✋ Na faixa da responsa

Essa edição **não** embute ferramentas de evasão de filtro / anti-censura / exploração
ofensiva — escolha nossa, tá no [`NOTICE.md`](NOTICE.md). SagaZ-ZeRo é pra construir,
automatizar e criar na responsa. Antes de ligar bot de Discord, confere
[`docs/DISCORD_MEMORY.md`](docs/DISCORD_MEMORY.md) e [`docs/GOD_MODE.md`](docs/GOD_MODE.md).

---

## 🫡 Créditos

- **Edição:** SagaZ-ZeRo · HooLeeSh33t Edition — **by dSant** (`@21daTitan`, _Systemia Solutions_)
- **Obra original:** **Cassandra**, criada por **Mörlsara** — _Morlsara Code Nexus_
- **Upstream:** https://github.com/DarkyHArry/cassandra-agent

Tamo junto. Jaé! 🤝

---

```bash
python3 -m unittest discover -s tests -q   # roda a bateria de testes
```
