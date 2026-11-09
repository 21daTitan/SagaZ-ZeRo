# ⬡⬢ HooLeeSh33t v0.2 — Deploy permanente em VPS

**Status:** Lançado
**Base travada:** commit da v0.1 (ver [`REPO-LOCK.md`](REPO-LOCK.md))
**Regra:** aditivo. Nenhum arquivo já resolvido foi tocado.

---

## O que entrou nesta versão

### `deploy-vps.sh` — instalador remoto pra VPS Linux (Ubuntu/Debian)

Um comando só, rodado DENTRO da VPS como root:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/21daTitan/SagaZ-ZeRo/main/deploy-vps.sh)
```

Faz tudo sozinho:

1. Clona/atualiza o repo em `/opt/sagaz-zero`
2. Cria um usuário de sistema `sagaz-zero` **sem privilégio de root**
3. Sobe um serviço **systemd** (`sagaz-zero.service`) — sobrevive a reboot
   e reinicia sozinho se cair
4. Tranca a porta interna do app (8080) pra só aceitar conexão local
5. Põe um proxy **nginx com usuário/senha** na porta pública (8888)

Resultado: acesso ao SagaZ-ZeRo de **qualquer rede** (wifi, dados móveis,
em qualquer lugar) via `http://SEU-IP:8888`, com login, rodando 24/7
independente do celular estar ligado ou conectado.

### ⚠️ Achado de segurança importante

O `web_ui.py` (já resolvido, não alterado) tem o toggle de shell
**ativo por padrão** via `CASSANDRA_ALLOW_SHELL=1`. Isso significa que,
sem cuidado, quem acessa a interface Web pode ligar a execução autônoma
de comandos no servidor.

O `deploy-vps.sh` mitiga isso de duas formas, sem tocar em `web_ui.py`:

- Inicia o serviço sempre com `--no-allow-shell` (desligado no boot —
  você liga manualmente pelo toggle da interface, se quiser, a cada sessão)
- Roda o processo como usuário `sagaz-zero` **sem root**, então mesmo que
  o shell seja ligado, os comandos executam com privilégio limitado —
  não dá root da VPS de graça

**A senha do proxy (nginx Basic Auth) é, na prática, a chave-mestra da
sua VPS** — quem a tem, pode conversar com o SagaZ-ZeRo e, se quiser,
ligar o shell. Trata ela como senha de root.

### Atualizar depois

O mesmo comando de instalação serve pra atualizar: ele faz `git fetch` +
`git reset --hard origin/main` no `/opt/sagaz-zero` e reinicia o serviço.
Rodar de novo é seguro (idempotente) — não duplica usuário, não pede
senha do proxy de novo se já existir.

### Comandos úteis na VPS

```bash
systemctl status sagaz-zero      # ver status
systemctl restart sagaz-zero     # reiniciar manualmente
journalctl -u sagaz-zero -f      # ver logs ao vivo
htpasswd /etc/nginx/.sagaz_htpasswd <usuario>   # trocar a senha do proxy
```

---

## O que NÃO foi tocado nesta versão

Tudo que já estava travado na v0.1 continua travado. `deploy-vps.sh` é
o único arquivo novo desta versão.

---

Ordem e Progresso. 🤙
