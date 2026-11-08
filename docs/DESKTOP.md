# Desktop & Sandbox (Fase 6) 🖥️📦

## Modo desktop (app)

A interface **HooLeeSh33t Matrix** roda como "app" abrindo no navegador:

```bash
python3 -m sagaz desktop            # sobe o servidor local e abre a Matrix
python3 -m sagaz desktop --port 8090
```

Ela sobe em `http://127.0.0.1:8080` e abre a janela. Para uma **janela dedicada**
(sem abas do navegador), rode como app do Chrome/Edge:

```bash
# Linux/Windows (Chrome/Chromium/Edge)
google-chrome --app=http://127.0.0.1:8080/apps/hooleesh33t-matrix-v1/
```

### App nativo (produção)

Para empacotar um executável de desktop de verdade, embrulhe a interface web com
**Tauri** (recomendado, leve) ou **Electron**. O app nativo só aponta para o
servidor local do SagaZ — a lógica continua no Core. Passos (resumo):

1. `python -m sagaz --web` sobe o backend em `127.0.0.1:8080`.
2. O shell Tauri/Electron carrega essa URL numa janela.
3. Empacota para `.AppImage`/`.exe`/`.dmg`.

> Isso exige toolchain de Node/Rust e é opcional — o `sagaz desktop` já entrega a
> experiência de app sem dependências extras.

## Sandbox de execução (container)

O agente pode rodar comandos **isolados em Docker**, com a raiz do projeto montada,
**sem rede por padrão**, limites de memória/CPU/processos, capacidades removidas e
mantendo a propriedade dos arquivos:

```bash
python3 -m sagaz agent "rode a suíte de testes" --allow exec --sandbox
```

- Sem `--sandbox`, o `run_command` roda direto na máquina (com a trava de confirmação).
- Com `--sandbox`, cada comando roda em `docker run --rm --network none --cap-drop ALL
  --security-opt no-new-privileges ...`. Para liberar rede dentro do container, isso
  é opt-in no código (`SandboxExec(allow_network=True)`).
- Se o Docker não estiver instalado, o agente **avisa e não executa** (nunca cai
  para execução sem isolamento).
- Imagem padrão: `python:3.12-slim` (troque com `SAGAZ_SANDBOX_IMAGE`).

**Quando usar o sandbox:** rodar código/comandos de terceiros, de um plugin não
auditado, ou qualquer coisa em que você não confia 100%. Para o seu próprio
projeto, o modo direto já basta.
