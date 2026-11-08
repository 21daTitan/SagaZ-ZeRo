# Agente de código SagaZ-ZeRo 🤖

O `sagaz agent` transforma o SagaZ num **agente de código** no estilo Claude Code:
o modelo propõe ferramentas, o agente executa **sob permissão e confirmação**, e
itera até resolver o objetivo. Tudo **local** — nada é exposto na rede.

## Usar

```bash
# conecte um provedor uma vez (console operador)
python3 -m sagaz operator          # /conectar → /testar

# agente só-leitura (padrão seguro): lê e busca, não altera nada
python3 -m sagaz agent "explique o que faz o arquivo sagaz/app.py"

# liberando poderes (cada escopo é explícito):
python3 -m sagaz agent "crie um teste para sagaz/pix.py" --allow fs.write
python3 -m sagaz agent "rode os testes e conserte o que falhar" --allow fs.write,exec
python3 -m sagaz agent "faça commit e push na branch de trabalho" --allow git.write
```

- Sem `--allow`, o agente fica **só-leitura** (`fs.read`, `git.read`).
- Ações de **escrita**, **execução** e **push** pedem **confirmação** no terminal
  (ou passe `--yes` para auto-confirmar — **use com cuidado**).
- Sem objetivo na linha de comando, abre o **modo interativo**.

## Escopos

| Escopo | Libera |
|---|---|
| `fs.read` | `fs_list`, `fs_read`, `fs_search`, `fs_stat` |
| `fs.write` | `fs_write`, `fs_edit` (com backup em `state/backups/`) |
| `exec` | `run_command` (trava destrutiva + confirmação) |
| `git.read` | `git_status`, `git_diff` |
| `git.write` | `git_branch`, `git_add`, `git_commit`, `git_push` (**sem force-push**) |

Toda ferramenta de arquivo é **confinada à raiz do projeto** (sem `..`, sem
caminho absoluto, sem symlink que escape). Credenciais do GitHub são as do seu
`git` local — **nenhum token é lido ou gravado** pelo agente.

## Plugins

Plugins **registram ferramentas** próprias. Ficam em `plugins/<nome>/plugin.json`:

```json
{
  "name": "wordcount",
  "version": "1.0.0",
  "scopes": ["fs.read"],
  "tools": [
    {
      "name": "wordcount_contar",
      "description": "Conta palavras de um texto.",
      "scope": "fs.read",
      "parameters": {"type": "object",
        "properties": {"texto": {"type": "string"}}, "required": ["texto"]},
      "entry": "handlers.py:contar"
    }
  ]
}
```

```bash
python3 -m sagaz plugin list
python3 -m sagaz plugin enable wordcount     # habilitar = confiar no código do plugin
python3 -m sagaz plugin disable wordcount
```

Regras: cada ferramenta só pode pedir um escopo **declarado** no `scopes` do
plugin; um plugin só carrega quando **habilitado**. Veja o modelo em
[`plugins/example-wordcount/`](../plugins/example-wordcount/).

> ⚠️ **Segurança:** habilitar um plugin executa o código Python dele no mesmo
> processo (sem sandbox). Para plugins de terceiros, rode em container. Ver
> [`docs/ROADMAP.md`](ROADMAP.md).

## Compatível com MCP

O SagaZ também é **servidor MCP** (endpoint `/mcp`, ferramentas só-leitura) e tem
`connectors/` como encaixe para agentes externos (Claude Code, Codex, Hermes,
OpenCode). Um plugin pode ser um servidor MCP externo plugado por aí.
