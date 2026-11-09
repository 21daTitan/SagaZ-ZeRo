#!/usr/bin/env bash
# ⬡ SagaZ-ZeRo — HooLeeSh33t EdiTioN by dSanT
# Launcher para Linux / macOS / Termux
# Base: Evil Cassandra por Mörlsara

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Carrega .env se existir
if [ -f .env ]; then
  set -a
  source .env
  set +a
fi

# Ativa venv se existir
if [ -f .venv/bin/activate ]; then
  source .venv/bin/activate
elif [ -f venv/bin/activate ]; then
  source venv/bin/activate
fi

MODE="${1:-}"

if [ "$MODE" = "web" ]; then
  PORT="${2:-8080}"
  echo ""
  echo "⬡ SagaZ-ZeRo · HooLeeSh33t EdiTioN"
  echo "  Interface Web em http://localhost:${PORT}"
  echo ""
  python3 web_ui.py --port "$PORT"
else
  echo ""
  echo "⬡ SagaZ-ZeRo · HooLeeSh33t EdiTioN · CLI"
  echo ""
  python3 agent.py "$@"
fi
