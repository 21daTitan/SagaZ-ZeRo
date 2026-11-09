# ⬡⬢ HooLeeSh33t v0.1 — Personas, Android rápido & instaladores desktop

**Status:** Lançado
**Base travada:** commit `72920f2` (ver [`REPO-LOCK.md`](REPO-LOCK.md))
**Regra:** tudo aqui é **aditivo**. Nenhum arquivo já resolvido foi tocado.

---

## O que entrou nesta versão

### 1. Sistema de Personas Visuais (SagaZ / ZeRo)

Mesmo executor, duas caras. `sagaz` e `zero` são o **mesmo agente** — o
rebranding é só cosmético, na exibição do terminal. Isso é implementado
num módulo totalmente separado (`sagaz_zero/persona_display.py` +
`sagaz_zero/persona_launcher.py`) que **observa** a saída do `agent.py` de
fora, sem importar ou alterar uma linha dele. Se você apagar esses dois
arquivos, o `agent.py` continua funcionando 100% igual — prova de que é
puramente aditivo.

| Persona | Cor | Vibe |
|---|---|---|
| **⬡ SagaZ** | Azul | O Abusado — carioca desenrolado, descontraído |
| **⬢ ZeRo** | Vermelho / Branco | O Sangue Frio — direto ao ponto, certeiro no alvo |

### Os 3 modos de exibição (ativos, independentes, sem conflito)

Você pode trocar o modo com `--persona-mode` ou a variável de ambiente
`SAGAZ_ZERO_PERSONA_MODE`. Os três modos são implementados como funções
**isoladas** no código — nenhum chama o outro, nenhum lê o estado do outro.
Trocar de modo nunca corrompe, atropela ou embaralha o comportamento dos
outros dois.

**Modo `action`** — a persona troca conforme o TIPO de ação que tá rolando:
- SagaZ aparece em raciocínio, conversa, busca na web
- ZeRo aparece em execução direta: chamada de ferramenta, skill, comando

```bash
SAGAZ_ZERO_PERSONA_MODE=action ./bin/sagaz
```

**Modo `command`** (padrão) — a persona é fixa pelo comando que você digitou:
- `./bin/sagaz` → sempre azul, sempre "abusado", a sessão toda
- `./bin/zero` → sempre vermelho/branco, sempre "sangue frio", a sessão toda

```bash
./bin/sagaz    # tudo azul
./bin/zero     # tudo vermelho/branco
```

**Modo `dual`** — as duas personas aparecem SEMPRE, uma embaixo da outra,
em todo gatilho de ação — efeito visual duplo:

```bash
SAGAZ_ZERO_PERSONA_MODE=dual ./bin/sagaz
```

### 2. Comandos novos: `sagaz` e `zero`

```
bin/sagaz        # Linux/macOS/Termux
bin/zero
bin/sagaz.bat    # Windows CMD
bin/zero.bat
bin/sagaz.ps1    # Windows PowerShell
bin/zero.ps1
```

Todos chamam o mesmo `agent.py` por baixo (via `sagaz_zero/persona_launcher.py`),
sem duplicar lógica nenhuma.

### 3. Guia de instalação rápida pro Android (Termux)

[`INSTALL-ANDROID.md`](INSTALL-ANDROID.md) — passo a passo testado na prática,
com a gambiarra documentada pra não travar compilando `pydantic-core`/`cryptography`
em Rust no meio do caminho. Tem um caminho RÁPIDO (CLI só) e um COMPLETO (Web).

### 4. Instaladores automáticos pra desktop

```
install.sh     # Linux/macOS
install.bat    # Windows CMD
install.ps1    # Windows PowerShell
```

Criam o ambiente virtual, instalam as dependências e deixam tudo pronto pra
rodar — sem tocar nos launchers `sagaz-zero.*` que já existiam.

### 5. Regras de preservação do repositório

[`REPO-LOCK.md`](REPO-LOCK.md) — trava formal do que já foi resolvido até o
commit `72920f2`. A partir de agora, toda funcionalidade nova entra como
**arquivo adicional**, nunca como edição do que já existe (salvo autorização
explícita em contrário).

---

## O que NÃO foi tocado nesta versão

- `agent.py`
- `web_ui.py`
- `cassandra/` (client, providers, filter, compact, environment, toolfetch, crypto, guard, **attribution.py**)
- `cassandra-skill/` (655+ skills)
- `sagaz-zero.sh` / `.bat` / `.ps1`
- `README.md` (só recebeu um apêndice no final, nada reescrito)
- `NOTICE-SAGAZ.md`
- `.env.example`, `requirements.txt`, `model.png`, `LICENSE`

---

## Arquitetura — por que isso não quebra nada

```
┌─────────────────────────────────────────────┐
│  bin/sagaz, bin/zero                         │  ← comandos novos
│       │                                      │
│       ▼                                      │
│  sagaz_zero/persona_launcher.py              │  ← abre agent.py como
│       │        (pty no POSIX /                  processo filho,
│       │         subprocess no Windows)           observa a saída
│       ▼                                      │
│  sagaz_zero/persona_display.py               │  ← decide o banner,
│       (3 modos isolados, sem estado           │     3 funções puras
│        compartilhado entre eles)              │     independentes
│                                               │
│  ════════════ FRONTEIRA ════════════         │
│                                               │
│  agent.py  (intocado)                        │  ← roda exatamente
│  web_ui.py (intocado)                        │     como antes
│  cassandra/ (intocado)                       │
└─────────────────────────────────────────────┘
```

---

## Assinatura

> *dSanT é o vibecodev desse GodMode. Deus Jeová Jireh é o Mestre dos
> Mestres — conheceis o caminho e o caminho vos libertará. Jesus é o
> caminho, a verdade e a cura.*
>
> — dSanT, 24 anos, RJ

---

**SagaZ é abusado. Zero é o Sangue Frio.**
Ordem e Progresso. 🤙
