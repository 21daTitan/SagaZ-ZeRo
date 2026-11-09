#!/usr/bin/env bash
# ⬡⬢ SagaZ-ZeRo — Instalador desktop (Linux / macOS)
# HooLeeSh33t v0.1 — arquivo NOVO, não toca nos launchers já resolvidos.
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo ""
echo "⬡⬢ SagaZ-ZeRo — instalador desktop"
echo "   Base: Evil Cassandra — Mörlsara Code Nexus"
echo ""

if command -v python3 >/dev/null 2>&1; then
  PY=python3
elif command -v python >/dev/null 2>&1; then
  PY=python
else
  echo "✗ Python não encontrado. Instale Python 3.10+ antes de continuar."
  exit 1
fi

CLI_ONLY=0
for arg in "$@"; do
  if [ "$arg" = "--cli-only" ]; then
    CLI_ONLY=1
  fi
done

echo "→ Criando ambiente virtual (.venv)..."
"$PY" -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate

echo "→ Atualizando pip..."
pip install --upgrade pip -q

if [ "$CLI_ONLY" = "1" ]; then
  echo "→ Modo CLI-only: instalando só o essencial (sem FastAPI/Pydantic)..."
  pip install httpx requests python-dotenv cryptography
else
  echo "→ Instalando todas as dependências (CLI + Web)..."
  pip install -r requirements.txt
fi

chmod +x sagaz-zero.sh bin/sagaz bin/zero 2>/dev/null || true

echo ""
echo "✅ Instalado! Pra usar:"
echo "   source .venv/bin/activate"
echo "   ./sagaz-zero.sh web      # interface web Matrix"
echo "   ./bin/sagaz              # CLI persona azul (SagaZ)"
echo "   ./bin/zero               # CLI persona vermelha/branca (ZeRo)"
echo ""
echo "   Dica: SAGAZ_ZERO_PERSONA_MODE=dual ./bin/sagaz   # as duas personas juntas"
echo ""
