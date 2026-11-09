# ⬡⬢ HooLeeSh33t v0.3 — Acesso direto + memória visível

**Status:** Lançado
**Base travada:** commit da v0.2 (ver [`REPO-LOCK.md`](REPO-LOCK.md))
**Regra:** uma edição em arquivo travado nesta versão, **explicitamente
autorizada pelo dSanT** no chat, registrada na tabela de exceções do
`REPO-LOCK.md`.

---

## O que entrou nesta versão

### 1. Acesso sem senha no proxy público (padrão novo)

`deploy-vps.sh` agora entra direto, sem pedir usuário/senha — a pedido
explícito. Pra religar a autenticação quando quiser:

```bash
SAGAZ_ZERO_REQUIRE_AUTH=1 bash <(curl -fsSL https://raw.githubusercontent.com/21daTitan/SagaZ-ZeRo/main/deploy-vps.sh)
```

**Isso significa:** qualquer pessoa com o link `http://SEU-IP:8888`
acessa o SagaZ-ZeRo — incluindo o botão de ligar shell mode (que executa
comando no servidor, com o usuário sem-root `sagaz-zero`). Sem senha,
o link em si é a única barreira. Não compartilha ele por aí.

### 2. Histórico visível ao voltar (exceção em `web_ui.py`)

O servidor sempre guardou a conversa inteira numa variável global
enquanto o processo roda — isso nunca foi o problema. O que faltava era
a TELA mostrar esse histórico de novo quando você recarregava a página
ou voltava depois.

Adicionado:
- `GET /api/history` — expõe a conversa já existente (não cria
  armazenamento novo, só lê o que já tinha)
- JS no carregamento da página que busca esse histórico e redesenha
  o chat, em vez de começar vazio

Essa foi a **única edição em arquivo travado** desta versão, e só
aconteceu porque você pediu diretamente e autorizou no momento — está
registrada com data, arquivo e motivo na tabela de exceções do
`REPO-LOCK.md`.

**Limitação que continua existindo:** se o serviço `systemd` reiniciar
(queda, `systemctl restart`, reboot da VPS), a conversa é perdida —
porque ela vive em memória RAM do processo, não em disco. O serviço
tem `Restart=always`, então só reinicia se cair de verdade (crash), não
por você sair e voltar. Se quiser que sobreviva até a reinícios, isso
exigiria persistir em arquivo/banco — outra edição em `web_ui.py`, seria
nova autorização se você quiser isso no futuro.

---

## O que NÃO foi tocado além do registrado

Tudo mais da v0.2 continua como estava. Só os dois pontos acima.

---

Ordem e Progresso. 🤙
