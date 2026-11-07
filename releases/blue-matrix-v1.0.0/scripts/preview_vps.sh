#!/usr/bin/env bash
# Rode no Termux, não na VPS. NÃO altera Core, sistema existente, firewall ou DNS.
set -euo pipefail
BRANCH='feature/hooleesh33t-blue-matrix-v1'
read -r -p 'IP público confirmado da VPS: ' IP
read -r -p 'Usuário SSH [root]: ' SSHUSER; SSHUSER="${SSHUSER:-root}"
read -r -p 'Porta SSH [22]: ' SSHPORT; SSHPORT="${SSHPORT:-22}"
case "$IP" in ''|*' '*|*'/'*) echo 'IP inválido'; exit 1;; esac
case "$SSHPORT" in ''|*[!0-9]*) echo 'Porta inválida'; exit 1;; esac
echo "[SagaZ] Conectando em $SSHUSER@$IP:$SSHPORT. Será instalado SOMENTE em /opt/sagaz-blue-matrix-preview."
ssh -p "$SSHPORT" -o ConnectTimeout=12 "$SSHUSER@$IP" bash -s -- "$BRANCH" <<'REMOTE'
set -euo pipefail
BRANCH="$1"
DIR='/opt/sagaz-blue-matrix-preview'
if ! command -v git >/dev/null || ! command -v python3 >/dev/null; then
  echo '[ERRO] Instale git e python3 na VPS.'; exit 1
fi
if [ ! -d "$DIR/.git" ]; then
  if [ -e "$DIR" ]; then echo '[BLOQUEADO] Diretório ocupado; não sobrescrevi.'; exit 1; fi
  git clone --quiet --depth 1 --branch "$BRANCH" https://github.com/21daTitan/SagaZ-ZeRo.git "$DIR"
else
  git -C "$DIR" pull --ff-only
fi
APP="$DIR/releases/blue-matrix-v1.0.0/server/sagaz_server.py"
if [ ! -f "$APP" ]; then echo '[ERRO] Release não encontrada no GitHub.'; exit 1; fi
if curl -sf --max-time 2 http://127.0.0.1:8765/healthz >/dev/null; then
  echo '[OK] Prévia já responde na porta 8765; não reiniciei.'
else
  mkdir -p "$DIR/var"
  nohup env SAGAZ_BIND=127.0.0.1 SAGAZ_PORT=8765 python3 "$APP" \
    >"$DIR/var/preview.log" 2>&1 </dev/null &
  echo $! >"$DIR/var/preview.pid"
  sleep 1
  curl -fsS --max-time 4 http://127.0.0.1:8765/healthz || { echo '[ERRO] Servidor não respondeu. Veja log.'; exit 1; }
fi
echo
printf '[OK] Prévia instalada. Sem alteração no Core atual.\n'
printf 'Acesso pelo Termux: ssh -N -L 8765:127.0.0.1:8765 usuario@IP\n'
REMOTE
