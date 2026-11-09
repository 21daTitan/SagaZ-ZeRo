#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════
# SagaZ-ZeRo — Deploy permanente em VPS (Ubuntu/Debian)
# HooLeeSh33t v0.2 — arquivo NOVO, aditivo.
#
# Roda isto DENTRO da VPS (como root), via SSH:
#   bash <(curl -fsSL https://raw.githubusercontent.com/21daTitan/SagaZ-ZeRo/main/deploy-vps.sh)
#
# O que ele faz:
#   1. Clona/atualiza o repo em /opt/sagaz-zero
#   2. Cria um usuário de sistema SEM privilégio de root pra rodar o serviço
#   3. Sobe um serviço systemd (sobrevive a reboot, reinicia se cair)
#   4. Trava a porta do app (8080) pra só aceitar conexão local
#   5. Põe um proxy nginx com usuário/senha na porta pública (8888)
#
# Resultado: você acessa http://SEU-IP:8888 de qualquer rede,
# com login, e o serviço continua rodando sozinho 24/7.
# ═══════════════════════════════════════════════════════════
set -e

REPO_URL="https://github.com/21daTitan/SagaZ-ZeRo.git"
INSTALL_DIR="/opt/sagaz-zero"
APP_PORT="8080"
PUBLIC_PORT="8888"
SERVICE_NAME="sagaz-zero"
SERVICE_USER="sagaz-zero"
# Login/senha no proxy público. Padrão: DESLIGADO (acesso direto,
# sem pedir nada) — a pedido explícito do dSanT. Pra religar depois:
#   SAGAZ_ZERO_REQUIRE_AUTH=1 bash <(curl -fsSL .../deploy-vps.sh)
REQUIRE_AUTH="${SAGAZ_ZERO_REQUIRE_AUTH:-0}"

if [ "$EUID" -ne 0 ]; then
  echo "✗ Roda como root (ou com sudo)."
  exit 1
fi

echo ""
echo "⬡⬢ SagaZ-ZeRo — deploy na VPS"
echo ""

# ── 1. Dependências do sistema ──────────────────────────────
echo "→ Instalando dependências do sistema..."
apt-get update -qq
apt-get install -y -qq python3 python3-venv python3-pip git nginx apache2-utils curl

# ── 2. Clona ou atualiza o repositório ──────────────────────
# (git recusa operar numa pasta que não é "dele" por padrão —
#  isso é esperado quando a pasta já existia de uma tentativa
#  anterior. Autoriza explicitamente este diretório.)
git config --global --add safe.directory "$INSTALL_DIR" 2>/dev/null || true

if [ -d "${INSTALL_DIR}/.git" ]; then
  echo "→ Repositório já existe em ${INSTALL_DIR}, atualizando..."
  cd "$INSTALL_DIR"
  git fetch origin
  git reset --hard origin/main
else
  echo "→ Clonando o repositório..."
  git clone "$REPO_URL" "$INSTALL_DIR"
  cd "$INSTALL_DIR"
fi

# ── 3. Usuário de sistema sem privilégios de root ───────────
if ! id -u "$SERVICE_USER" >/dev/null 2>&1; then
  echo "→ Criando usuário de sistema '${SERVICE_USER}' (sem login, sem root)..."
  useradd --system --home "$INSTALL_DIR" --shell /usr/sbin/nologin "$SERVICE_USER"
fi

# ── 4. Ambiente virtual + dependências Python ───────────────
echo "→ Instalando dependências Python (venv)..."
python3 -m venv "${INSTALL_DIR}/.venv"
"${INSTALL_DIR}/.venv/bin/pip" install --upgrade pip -q
"${INSTALL_DIR}/.venv/bin/pip" install -r "${INSTALL_DIR}/requirements.txt" -q

# ── 5. .env (só cria se ainda não existir, nunca sobrescreve) ─
if [ ! -f "${INSTALL_DIR}/.env" ]; then
  cp "${INSTALL_DIR}/.env.example" "${INSTALL_DIR}/.env"
  echo "→ .env criado. Configure sua API key depois, direto na interface"
  echo "  (⚙ Configurações) ou editando ${INSTALL_DIR}/.env"
fi

chown -R "${SERVICE_USER}:${SERVICE_USER}" "$INSTALL_DIR"

# ── 6. Serviço systemd ───────────────────────────────────────
echo "→ Configurando serviço systemd..."
cat > "/etc/systemd/system/${SERVICE_NAME}.service" << EOF
[Unit]
Description=SagaZ-ZeRo HooLeeSh33t EdiTioN — Web UI
After=network.target

[Service]
Type=simple
User=${SERVICE_USER}
Group=${SERVICE_USER}
WorkingDirectory=${INSTALL_DIR}
EnvironmentFile=-${INSTALL_DIR}/.env
ExecStart=${INSTALL_DIR}/.venv/bin/python web_ui.py --port ${APP_PORT} --no-allow-shell
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable "$SERVICE_NAME" >/dev/null 2>&1
systemctl restart "$SERVICE_NAME"
sleep 1
systemctl is-active --quiet "$SERVICE_NAME" && echo "→ Serviço ativo e rodando." || {
  echo "✗ Serviço não subiu. Veja: journalctl -u ${SERVICE_NAME} -n 50"
  exit 1
}

# ── 7. Tranca a porta do app pra só aceitar conexão local ────
# ORDEM IMPORTA: "iptables -I" sem número sempre insere no TOPO da
# fila. Inserir ACCEPT e depois DROP faz o DROP ficar por cima do
# ACCEPT — bloqueando TUDO, até o próprio localhost (bug real já
# visto em produção). O jeito certo: insere o DROP primeiro (vai
# pro topo), depois o ACCEPT (vai pro topo de novo, empurrando o
# DROP pra baixo) — resultado final: ACCEPT checado ANTES do DROP.
echo "→ Travando porta ${APP_PORT} pra acesso local apenas..."
iptables -D INPUT -i lo -p tcp --dport "$APP_PORT" -j ACCEPT 2>/dev/null || true
iptables -D INPUT -p tcp --dport "$APP_PORT" -j DROP 2>/dev/null || true
iptables -I INPUT -p tcp --dport "$APP_PORT" -j DROP
iptables -I INPUT -i lo -p tcp --dport "$APP_PORT" -j ACCEPT

if command -v netfilter-persistent >/dev/null 2>&1; then
  netfilter-persistent save >/dev/null 2>&1 || true
elif [ -d /etc/iptables ]; then
  iptables-save > /etc/iptables/rules.v4 2>/dev/null || true
fi

# Confirma de verdade que o próprio localhost ainda alcança a porta
# — se isso falhar aqui, é bug de regra/ordem de firewall, não de
# rede externa, e é melhor parar o deploy do que deixar passar.
if ! curl -fsS -o /dev/null -m 5 "http://127.0.0.1:${APP_PORT}/"; then
  echo "✗ A porta ${APP_PORT} ficou inacessível até pra localhost depois do"
  echo "  firewall. Isso é bug de regra de iptables, não de rede. Rodando:"
  echo "    iptables -L INPUT -n --line-numbers | grep ${APP_PORT}"
  iptables -L INPUT -n --line-numbers | grep "$APP_PORT" || true
  exit 1
fi

# ── 8. Proxy público (nginx) — com ou sem login, conforme REQUIRE_AUTH ──
AUTH_BLOCK=""
if [ "$REQUIRE_AUTH" = "1" ]; then
  if [ ! -s /etc/nginx/.sagaz_htpasswd ]; then
    echo ""
    echo "→ Define um usuário e senha pra proteger o acesso público:"
    read -rp "   Usuário: " AUTH_USER
    until htpasswd -c /etc/nginx/.sagaz_htpasswd "$AUTH_USER"; do
      echo "  Não bateu, tenta de novo (as duas senhas digitadas precisam ser iguais)."
    done
  else
    echo "→ Login já configurado (pra trocar depois: htpasswd /etc/nginx/.sagaz_htpasswd <usuario>)"
  fi
  AUTH_BLOCK=$'    auth_basic "SagaZ-ZeRo — HooLeeSh33t EdiTioN";\n    auth_basic_user_file /etc/nginx/.sagaz_htpasswd;'
else
  echo "→ Acesso direto, sem login (REQUIRE_AUTH=0) — exposto a qualquer um com o link."
  rm -f /etc/nginx/.sagaz_htpasswd 2>/dev/null || true
fi

# Remove o site padrão do nginx — ele escuta na porta 80 por padrão,
# e se já tiver outra coisa (Traefik, por exemplo) usando a 80 nessa
# VPS, isso derruba o nginx inteiro antes de chegar na nossa porta
# (8888), que é a única que a gente realmente usa aqui.
rm -f /etc/nginx/sites-enabled/default

cat > /etc/nginx/sites-available/sagaz-zero << EOF
server {
    listen ${PUBLIC_PORT};
    server_name _;

${AUTH_BLOCK}

    location / {
        proxy_pass http://127.0.0.1:${APP_PORT};
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_buffering off;
        proxy_cache off;
        chunked_transfer_encoding off;
        proxy_read_timeout 600s;
    }
}
EOF

ln -sf /etc/nginx/sites-available/sagaz-zero /etc/nginx/sites-enabled/sagaz-zero
nginx -t
systemctl restart nginx
systemctl is-active --quiet nginx && echo "→ nginx ativo." || {
  echo "✗ nginx não subiu. Veja: journalctl -xeu nginx.service -n 30 --no-pager"
  exit 1
}

PUBLIC_IP=$(curl -fsSL -4 ifconfig.me 2>/dev/null || hostname -I | awk '{print $1}')

echo ""
echo "✅ SagaZ-ZeRo rodando permanentemente na VPS."
echo ""
echo "   Acesse de QUALQUER rede (wifi, dados móveis, o que for):"
echo "   http://${PUBLIC_IP}:${PUBLIC_PORT}"
echo ""
if [ "$REQUIRE_AUTH" = "1" ]; then
  echo "   Login: o usuário/senha que você definiu agora."
else
  echo "   Sem login — entra direto. QUALQUER UM com esse link também entra."
  echo "   Pra ligar a senha depois: SAGAZ_ZERO_REQUIRE_AUTH=1 bash <(curl -fsSL .../deploy-vps.sh)"
fi
echo ""
echo "   ⚠️  O botão de shell na interface, se você ligar, executa"
echo "      comandos como o usuário '${SERVICE_USER}' (sem root)."
if [ "$REQUIRE_AUTH" = "1" ]; then
  echo "      Quem tem a senha de login tem esse poder — guarda bem."
else
  echo "      Sem login, QUALQUER UM com o link tem esse poder."
fi
echo ""
echo "   Pra atualizar depois (puxa do GitHub e reinicia sozinho):"
echo "   bash <(curl -fsSL https://raw.githubusercontent.com/21daTitan/SagaZ-ZeRo/main/deploy-vps.sh)"
echo ""
echo "   Comandos úteis:"
echo "     systemctl status ${SERVICE_NAME}     # ver status"
echo "     systemctl restart ${SERVICE_NAME}    # reiniciar"
echo "     journalctl -u ${SERVICE_NAME} -f     # ver logs ao vivo"
echo ""
