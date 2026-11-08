# UPSTREAM.md — Ponte de atualização SagaZ-ZeRo ⇄ Cassandra

Rotina para incorporar melhorias do **Cassandra** (obra original de **Mörlsara**,
*Morlsara Code Nexus*) na edição **SagaZ-ZeRo · HooLeeSh33t Edition by dSant**
**sem perder as customizações** e **sem apagar a proveniência original**.

> Guia doutrinário completo: [`docs/MASTER-PROMPT-SAGAZ.md`](MASTER-PROMPT-SAGAZ.md).

---

## 0. Relação entre os repositórios (leia antes de tudo)

- **origin** → `https://github.com/21daTitan/SagaZ-ZeRo` (repo do operador; **já configurado — não sobrescrever**).
- **upstream** → `https://github.com/DarkyHArry/cassandra-agent` (obra original).
- **Branch de trabalho da edição:** `claude/whimsical-roleplay-b5f30q` (atual). A branch padrão do operador é `main`.

**Fato que muda o fluxo:** conforme `FORK.md` e `NOTICE.md`, o SagaZ-ZeRo é uma
**implementação independente inspirada** no Cassandra — **não** um fork Git que
compartilha o histórico nem o código-fonte do upstream. Portanto:

- ❌ **NÃO** faça `git merge upstream/<branch>` direto: os históricos são
  **não relacionados**, e unir históricos não relacionados automaticamente é
  proibido (ver Master Prompt §2 e §8).
- ✅ A ponte aqui é **revisar-e-portar seletivo**: comparar árvores, escolher as
  mudanças funcionais verificadas e aplicá-las à mão na edição, preservando
  identidade, compatibilidade e proveniência.

### Base upstream — estado confirmado nesta entrega

- O snapshot recebido veio por **ZIP** (`Cassandra-v3.1.zip`, raiz
  `cassandra-agent-main/`), que **não contém histórico Git**.
- Pista de base no comentário do ZIP: `9c7bfba7a66df184de70904c2d87acc45aec0eaa`.
- **Limitação:** esse commit **não foi confirmado** contra
  `DarkyHArry/cassandra-agent` nesta sessão (o upstream não esteve acessível ao
  ambiente). Trate o SHA apenas como pista. **Não** se fabricou ancestralidade:
  nenhuma linhagem Git com o Cassandra foi inventada. Confirme o SHA e compare a
  árvore antes de adotá-lo como base (passo 2).

---

## 1. Pré-requisitos (uma vez)

```bash
# Inspecione os remotes ANTES de mexer (não sobrescreva origin)
git remote -v

# Adicione o upstream como REMOTE SOMENTE-LEITURA (nome 'upstream')
git remote add upstream https://github.com/DarkyHArry/cassandra-agent.git

# Descubra a branch padrão do upstream (NÃO presuma 'main')
git remote show upstream | sed -n 's/.*HEAD branch: //p'

# (opcional) reaproveitar resoluções de conflito manuais — exige revisão depois
git config rerere.enabled true
```

`git rerere` memoriza como você resolveu um conflito e reaplica a mesma resolução
se o mesmo conflito reaparecer. **Reaproveita, não aprova:** toda reaplicação
ainda precisa ser revisada antes do commit.

---

## 2. Confirmar a base e comparar a árvore

```bash
git fetch upstream
UPSTREAM_DEFAULT="$(git remote show upstream | sed -n 's/.*HEAD branch: //p')"

# Confirme a pista de base (se existir no upstream)
git cat-file -t 9c7bfba7a66df184de70904c2d87acc45aec0eaa 2>/dev/null \
  && git show --stat 9c7bfba7a66df184de70904c2d87acc45aec0eaa | head -40 \
  || echo "SHA não encontrado no upstream — registre a limitação, não adote como base."

# Relatório de compatibilidade entre uma checkout do upstream e a edição
#   (usa o mecanismo próprio do projeto; é só leitura, não altera nada)
git worktree add /tmp/cassandra-upstream upstream/"$UPSTREAM_DEFAULT"
python3 -m sagaz compat /tmp/cassandra-upstream --local . > docs/_upstream-compat.md
git worktree remove /tmp/cassandra-upstream
```

Leia `docs/_upstream-compat.md`: ele lista o que mudou por arquivo e orienta
**quais** diferenças funcionais valem portar.

---

## 3. Branch de sincronização e porte seletivo

```bash
# 1) Árvore limpa
git status --porcelain            # deve estar vazio
git switch claude/whimsical-roleplay-b5f30q

# 2) Registre o ponto anterior (âncora para reverter se preciso)
git rev-parse HEAD > .sync-base.txt

# 3) Branch de sync a partir da EDIÇÃO (nunca a partir do upstream)
git switch -c sync/upstream-$(date +%Y%m%d)

# 4) Porte seletivo: traga só os arquivos/áreas funcionais verificados.
#    Ex.: um módulo novo do core que não toca identidade:
git checkout upstream/"$UPSTREAM_DEFAULT" -- cassandra/<arquivo-funcional>.py
#    Reescreva/adapte a identidade visível conforme o Master Prompt (§1, §6).
#    NUNCA use 'git checkout upstream -- .' nem resolução global ours/theirs.
```

**Em cada conflito/porte:** preserve a identidade **SagaZ-ZeRo**, a
compatibilidade (`CASSANDRA_*`, `CassandraClient`, launchers, endpoints) e a
proveniência (`Morlsara Code Nexus`), **incorporando** a melhoria funcional do
upstream. Nunca descarte o arquivo inteiro de um lado automaticamente.

---

## 4. Validar antes de integrar

```bash
# Sintaxe dos .py alterados
python3 -m py_compile $(git diff --name-only --diff-filter=ACM 'sagaz/*.py' 'cassandra/*.py')

# Testes (pytest não é exigido; o projeto roda com unittest)
python3 -m unittest discover -s tests -q

# Proveniência (marca original + separação de créditos)
python3 -m unittest tests.test_provenance -q
python3 dsant.py doctor

# Identidade no prompt efetivo e interfaces tocadas
python3 -m sagaz operator   # TUI: /status, /skills, /sair
# (web) python3 -m sagaz --web --port 8080  → só via túnel SSH, nunca exposto
```

## 5. Revisar o diff e integrar

```bash
git diff claude/whimsical-roleplay-b5f30q...HEAD    # revise TUDO
git switch claude/whimsical-roleplay-b5f30q
git merge --no-ff sync/upstream-AAAAMMDD            # fast-forward desligado
```

## 6. Abortar / reverter

```bash
git merge --abort                 # aborta um merge pendente (nada é integrado)
git revert -m 1 <sha-do-merge>    # reverte integração JÁ publicada, sem reescrever história
# Proibido: force push, reset --hard destrutivo, git clean -fd em branch alheia.
```

---

## 7. Áreas customizadas por dSant (preservar sempre)

| Área | Arquivos |
|---|---|
| Identidade / créditos | `sagaz/attribution.py`, `NOTICE.md`, `FORK.md`, `THIRD_PARTY_NOTICES.md`, `README*.md`, `docs/SAGAZ.md` |
| Interface | `sagaz/operator_tui.py`, `sagaz/app.py`, `releases/blue-matrix-*/apps/hooleesh33t-matrix-*` |
| Skills adicionais | `.agents/skills/discord-memory`, `.agents/skills/cti-intelligence`, perfis `sagaz/god.py` |
| Core / provedor | `sagaz/provider_config.py`, `sagaz/ai_session.py`, `sagaz/gateway/*` |
| Ponte / compat | `sagaz/compat/upstream.py`, este `docs/UPSTREAM.md` |

## 8. Limites honestos

- Este fluxo **reduz** o trabalho de atualização; **não garante** ausência de
  conflitos futuros nem compatibilidade automática.
- Como não há ancestralidade Git compartilhada, cada atualização é um **porte
  revisado**, não um merge mecânico.
- Nenhuma automação publica ou integra atualização sozinha — por decisão de
  projeto, a v1 usa **Git + esta documentação**, não um script de sync.
