# ⬡ SagaZ-ZeRo — HooLeeSh33t EdiTioN by dSanT

<div align="center">

```
╔══════════════════════════════════════════════════════╗
║   ⬡  SagaZ-ZeRo · HooLeeSh33t EdiTioN by dSanT  ⬡  ║
║          Baseado em Evil Cassandra — Mörlsara        ║
╚══════════════════════════════════════════════════════╝
```

[![Python](https://img.shields.io/badge/Python-3.10%2B-00f5ff?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-async-00f5ff?style=flat-square)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/Licença-MIT-00b8cc?style=flat-square)](LICENSE)
[![Base](https://img.shields.io/badge/Base-Evil%20Cassandra-005a65?style=flat-square)](https://github.com/DarkyHArry/cassandra-agent)

**Agente de IA multi-provedor com interface Web Matrix cyan e CLI de terminal.**  
BYOK (Bring Your Own Key) — você traz a chave, a gente faz a magia rolar.

</div>

---

## 🎯 O que é isso?

Sabe quando você quer um agente de IA que conecta em **qualquer provedor** — OpenAI, DeepSeek, xAI Grok, Anthropic, Gemini, OpenRouter, Ollama local — sem depender de um único serviço?

É isso. SagaZ-ZeRo é um **cliente de terminal + interface web** que você sobe localmente, bota sua chave API e conversa. Sem middleman, sem pagar além da API que você já tem.

Base técnica: **Evil Cassandra** de [Mörlsara — Morlsara Code Nexus](https://github.com/DarkyHArry/cassandra-agent), que é uma das implementações mais completas que eu já vi. Peguei, dei um rebrand com tema Matrix ciano, rolei a interface nova e lancei como **HooLeeSh33t EdiTioN**.

Créditos completos no arquivo [`cassandra/attribution.py`](cassandra/attribution.py) — não tiro crédito de ninguém, família.

---

## ⚡ Features

- 🌐 **Multi-provedor real** — OpenAI, DeepSeek, xAI/Grok, Anthropic, Gemini, OpenRouter, Ollama e outros compatíveis com o formato OpenAI Chat Completions
- 💻 **CLI de terminal** — `agent.py` com cores ciano Matrix, streaming SSE, spinner de loading
- 🖥️ **Web UI Matrix** — interface no navegador com Matrix rain animation, tema ciano, responsivo desktop/mobile
- 🔑 **BYOK** — Bring Your Own Key. Você configura suas chaves, nenhuma credencial vai a lugar nenhum por padrão
- 🧠 **Skillogy** — sistema de skills/instruções carregáveis (pasta `cassandra-skill/`)
- 🔒 **Shell mode** — execução de comandos desativada por padrão. Ativa com `--allow-shell` só se souber o que tá fazendo
- 📡 **Streaming** — respostas em tempo real via SSE
- 🗜️ **Compactação de contexto** — contexto longo é compactado automaticamente pra economizar tokens
- 🛠️ **Tool fetch** — baixa ferramentas sob demanda quando o agente solicita

---

## 🚀 Instalação rápida

### Pré-requisitos
- Python 3.10 ou superior
- `pip` atualizado

### Clone e roda

```bash
# Clona o repo
git clone https://github.com/21daTitan/SagaZ-ZeRo.git
cd SagaZ-ZeRo

# Cria venv (recomendado)
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows

# Instala dependências
pip install -r requirements.txt

# Copia e edita o .env
cp .env.example .env
# Edita o .env com suas chaves API

# Roda a interface web (abre em http://localhost:8080)
./sagaz-zero.sh web
# ou
python web_ui.py --web

# Roda o CLI de terminal
./sagaz-zero.sh
# ou
python agent.py
```

### Windows

```powershell
.\sagaz-zero.bat web   # interface web
.\sagaz-zero.bat       # CLI terminal
```

```powershell
.\sagaz-zero.ps1 web   # PowerShell
```

---

## ⚙️ Configuração

Copie `.env.example` para `.env` e preencha com suas chaves:

```env
# Exemplo com OpenAI
SAGAZ_ZERO_API_KEY=sk-...
SAGAZ_ZERO_BASE_URL=https://api.openai.com/v1
SAGAZ_ZERO_MODEL=gpt-4o

# Exemplo com DeepSeek
SAGAZ_ZERO_API_KEY=sk-...
SAGAZ_ZERO_BASE_URL=https://api.deepseek.com/v1

# Exemplo com xAI Grok
SAGAZ_ZERO_API_KEY=xai-...
SAGAZ_ZERO_BASE_URL=https://api.x.ai/v1

# Variáveis CASSANDRA_* também são reconhecidas (compatibilidade)
```

Ou configure diretamente na interface web em **⚙ Configurações** sem precisar editar arquivos.

---

## 🌐 Interface Web

Sobe o servidor e acessa no navegador:

```
http://localhost:8080
```

A interface tem:
- **Matrix rain** na tela (tipo o filme, sabe né)
- Seleção de provider e modelo na barra superior
- Chat com streaming em tempo real
- Configuração de chave API inline (fica salvo na sessão)
- Toggle de shell mode
- Responsivo em mobile

---

## 💻 CLI de Terminal

```bash
# Modo interativo padrão
python agent.py

# Com shell habilitado (cuidado!)
python agent.py --allow-shell

# Apontar pra um provedor específico
python agent.py --provider deepseek --model deepseek-chat

# Usar porta diferente na web
python agent.py --web --port 9090
```

Dentro do CLI:
- `:sair` — encerra
- `:limpar` — limpa o histórico da conversa
- `:log` — mostra o log de atividade
- `:skill <nome>` — carrega uma skill específica

---

## 🔌 Provedores suportados

| Provider | Base URL padrão |
|---|---|
| OpenAI | `https://api.openai.com/v1` |
| DeepSeek | `https://api.deepseek.com/v1` |
| xAI / Grok | `https://api.x.ai/v1` |
| Anthropic | `https://api.anthropic.com/v1` (via proxy compat) |
| Gemini | `https://generativelanguage.googleapis.com/v1beta/openai` |
| OpenRouter | `https://openrouter.ai/api/v1` |
| Ollama (local) | `http://localhost:11434/v1` |
| Qualquer OpenAI-compat | URL customizável |

---

## 📁 Estrutura

```
SagaZ-ZeRo/
├── agent.py              # CLI de terminal (entrada principal)
├── web_ui.py             # Servidor web FastAPI
├── cassandra/            # Núcleo técnico (preservado integralmente)
│   ├── client.py         # CassandraClient multi-provedor
│   ├── providers.py      # Catálogo de provedores
│   ├── filter.py         # Filtros e proteções
│   ├── compact.py        # Compactação de contexto
│   ├── environment.py    # Ambiente e skills
│   ├── toolfetch.py      # Download de ferramentas sob demanda
│   ├── crypto.py         # Criptografia
│   ├── guard.py          # Proteções
│   └── attribution.py    # Créditos do autor original ← NÃO ALTERAR
├── cassandra-skill/      # 655+ arquivos de skill
├── sagaz_zero/           # Alias de compatibilidade
├── sagaz-zero.sh         # Launcher Linux/macOS
├── sagaz-zero.bat        # Launcher Windows CMD
├── sagaz-zero.ps1        # Launcher Windows PowerShell
├── requirements.txt
├── .env.example
└── NOTICE-SAGAZ.md       # Créditos desta edição
```

---

## ⚠️ Aviso importante

**Shell mode desativado por padrão.** Se você habilitar `--allow-shell`, o agente pode executar comandos no seu sistema sem pedir confirmação. Use só se souber o que tá fazendo e em ambiente controlado.

**BYOK:** Nenhuma chave API é incluída. Você é responsável pelas suas credenciais. Não commita `.env` com chaves reais.

---

## 🏆 Créditos e agradecimentos

**Base técnica:** [Evil Cassandra](https://github.com/DarkyHArry/cassandra-agent) por **Mörlsara — Morlsara Code Nexus**  
Todo o núcleo multi-provedor, streaming SSE, sistema de skills, compactação de contexto e arquitetura é obra do Mörlsara. Bora dar o crédito onde é devido.

**Esta edição:** dSanT — HooLeeSh33t EdiTioN  
Rebrand visual, interface web Matrix cyan, launchers e ajustes de identidade.

---

## 📄 Licença

Veja o arquivo [`LICENSE`](LICENSE) para a licença do projeto base.  
Esta edição (SagaZ-ZeRo HooLeeSh33t EdiTioN) não é uma publicação oficial do autor original.

---

<div align="center">

```
⬡ SagaZ-ZeRo · HooLeeSh33t EdiTioN by dSanT ⬡
Feito no RJ · Base: Evil Cassandra — Mörlsara Code Nexus
```

</div>
