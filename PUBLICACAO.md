# Publicar SagaZ ZeRo v3.7.0 sem sobrescrever arquivos existentes

Destino informado: `https://github.com/21daTitan/SagaZ-ZeRo`.

O pacote local **não tem acesso autenticado de escrita ao GitHub**. Nenhum commit, push ou alteração remota foi realizado nesta entrega. Antes de importar, use uma **branch separada** e preserve o histórico existente.

## Método A — GitHub Codespaces no celular

No GitHub, abra o repositório > **Code > Codespaces** (caso esteja disponível em seu plano). Envie o arquivo `SagaZ-ZeRo-3.7.0-zeRo.zip` para o Codespace. Em terminal do Codespace (dentro da raiz do repositório):

```bash
git switch -c sagaz-v3.7.0-revisao
python3 - <<'PY'
import zipfile
with zipfile.ZipFile('SagaZ-ZeRo-3.7.0-zeRo.zip') as z:
    z.extract('SagaZ-ZeRo-v3.7.0-zeRo/tools/safe_merge.py', '/tmp/sagaz-importer')
PY
python3 /tmp/sagaz-importer/SagaZ-ZeRo-v3.7.0-zeRo/tools/safe_merge.py SagaZ-ZeRo-3.7.0-zeRo.zip .
python3 /tmp/sagaz-importer/SagaZ-ZeRo-v3.7.0-zeRo/tools/safe_merge.py SagaZ-ZeRo-3.7.0-zeRo.zip . --apply
python3 -m unittest discover -s tests -v
python3 tools/audit_bytes.py --strict
git status --short
```

O importador inclui apenas **arquivos que não existiam** e lista conflitos. Antes de commitar, revise os conflitos e as diferenças desejadas; arquivos iguais não são sobrescritos. O ZIP dentro da raiz não deve entrar no commit:

```bash
git add -A -- ':!SagaZ-ZeRo-3.7.0-zeRo.zip'
git commit -m 'feat: integrate verified SagaZ ZeRo v3.7.0 components'
git push -u origin sagaz-v3.7.0-revisao
```

Depois, crie um pull request no GitHub. Nenhuma alteração atinge a branch principal sem a revisão.

## Método B — Termux com git já autenticado

Extraia o ZIP na pasta Downloads, instale `python` e `git` no Termux e siga o fluxo de clone/merge. O helper `tools/publish_termux.sh` do ZIP cria uma branch nova, importa sem sobrescrever, faz commit e push **apenas após invocação explícita**.

```bash
bash tools/publish_termux.sh /caminho/SagaZ-ZeRo-3.7.0-zeRo.zip https://github.com/21daTitan/SagaZ-ZeRo.git
```

**Revisão obrigatória:** o helper não resolve conflitos, não rebaseia silenciosamente, não apaga arquivos e não transforma tokens/assinaturas ChatGPT em credenciais Git.

## Integridade do ZIP

O arquivo `SHA256SUMS` acompanha o pacote, com um hash real do ZIP. Após baixar ambos no mesmo diretório, `sha256sum -c SHA256SUMS` deve retornar OK. Testes dos arquivos que forem importados devem ser repetidos na árvore Git real.
