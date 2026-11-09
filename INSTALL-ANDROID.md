# 📱 Instalação no Android via Termux — modo bandalha, mas liso

Pai, rodar isso no celular tem umas pegadinha chata — vou te passar o caminho
testado, já com as gambiarra resolvida, pra você não perder tempo igual nós
perdemos. Segue o fluxo e copia os comandos na ordem.

---

## ⚡ Passo 0 — Instale o Termux certo

Baixa o Termux pelo **F-Droid**, não pela Play Store (a versão da Play Store
tá abandonada e dá problema de repositório):

👉 https://f-droid.org/packages/com.termux/

---

## 🚀 Caminho RÁPIDO — só o CLI de terminal (recomendado pra testar liso)

Esse caminho não precisa compilar nada pesado. Sobe em 2 minutos.

```bash
# Atualiza o Termux
pkg update -y && pkg upgrade -y

# Instala o essencial (python já vem com o binário 'python', não 'python3')
pkg install -y python git python-cryptography

# Clona o repo
git clone https://github.com/21daTitan/SagaZ-ZeRo.git
cd SagaZ-ZeRo

# Instala só o que o CLI precisa (sem FastAPI/Pydantic = sem dor de cabeça)
pip install httpx requests python-dotenv

# Roda o CLI
python agent.py
```

Se der `python3: command not found` em qualquer launcher `.sh`, roda:

```bash
echo "alias python3=python" >> ~/.bashrc && source ~/.bashrc
```

---

## 🌐 Caminho COMPLETO — com interface Web (demora mais, mas vale)

A interface Web precisa de `fastapi` + `pydantic` + `uvicorn`, e o
`pydantic-core` compila em **Rust**. No celular isso demora uns minutos
(parece que travou — não travou, só tá compilando de verdade). Faz assim:

```bash
pkg update -y && pkg upgrade -y
pkg install -y python git rust binutils python-cryptography

git clone https://github.com/21daTitan/SagaZ-ZeRo.git
cd SagaZ-ZeRo

pip install -r requirements.txt
```

> ⏳ A instalação do `pydantic` vai parecer "pendurada" por uns minutos —
> é o Rust compilando o `pydantic-core` pro processador ARM do seu celular.
> Deixa rolar, não cancela.

Depois disso:

```bash
python web_ui.py --port 8080
```

Abre `http://localhost:8080` no navegador do celular.

---

## 🩹 Deu erro? Solução rápida dos problemas mais comuns

| Erro | Causa | Solução |
|---|---|---|
| `python3: command not found` | Termux só tem `python`, não `python3` | `echo "alias python3=python" >> ~/.bashrc && source ~/.bashrc` |
| `Failed to build 'cryptography'` | Falta compilador Rust | `pkg install python-cryptography` (já vem compilado, não precisa de Rust) |
| `Failed to build 'pydantic-core'` / menciona `maturin` / `rustup` | Falta Rust no sistema | `pkg install rust` e tenta o `pip install` de novo |
| `ImportError: cannot import name 'TypeAdapter' from 'pydantic'` | Você instalou `pydantic<2` mas o FastAPI instalado já exige Pydantic v2 | `pip uninstall -y pydantic fastapi starlette` e depois `pip install pydantic fastapi uvicorn` (agora com Rust instalado, compila certo) |
| `No command 'sagaz'/'zero' found` | Os binários `bin/sagaz` e `bin/zero` não tão no PATH | Roda direto: `./bin/sagaz` ou `./bin/zero` de dentro da pasta do projeto |

---

## 🎭 Depois de instalado — testando as personas

```bash
chmod +x bin/sagaz bin/zero
./bin/sagaz      # persona azul, descontraído
./bin/zero       # persona vermelho/branco, direto ao ponto

# Quer as duas juntas, empilhadas?
SAGAZ_ZERO_PERSONA_MODE=dual ./bin/sagaz
```

Detalhes completos do sistema de personas: veja [`HOOLEESH33T-v0.1.md`](HOOLEESH33T-v0.1.md).

---

## 💾 Dica extra: mantendo a sessão viva

Se o Android matar o processo quando a tela apaga, instala o `termux-wake-lock`:

```bash
pkg install termux-api
termux-wake-lock
```

E pra persistir entre reinícios do Termux, usa `tmux`:

```bash
pkg install tmux
tmux new -s sagaz
# dentro do tmux, roda o sagaz-zero normalmente
# pra sair sem matar: Ctrl+B depois D
# pra voltar: tmux attach -t sagaz
```

---

Jaé! Qualquer erro que não tá na tabela, abre uma issue no repo que a gente
resolve. 🤙
