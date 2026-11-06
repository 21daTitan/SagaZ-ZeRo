#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO='https://github.com/21daTitan/SagaZ-ZeRo.git'
BRANCH='feature/hooleesh33t-blue-matrix-v1'
DEST='releases/blue-matrix-v1.0.0'
command -v git >/dev/null || { echo '[ERRO] Instale git no Termux: pkg install git'; exit 1; }
if find "$ROOT" -name .env -o -name '*.pem' -o -name '*.key' | grep -q .; then
  echo '[BLOQUEADO] Há arquivos potencialmente sensíveis no pacote.'; exit 1
fi
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT
echo "[SagaZ] Clonando repositório: $REPO"
git clone --quiet "$REPO" "$STAGE/repo"
cd "$STAGE/repo"
if git show-ref --verify --quiet "refs/heads/$BRANCH" || git ls-remote --exit-code origin "refs/heads/$BRANCH" >/dev/null 2>&1; then
  echo "[BLOQUEADO] Branch já existe: $BRANCH. Revise antes de substituir."; exit 1
fi
if [ -e "$DEST" ]; then echo "[BLOQUEADO] $DEST já existe no repositório."; exit 1; fi
git switch -c "$BRANCH" >/dev/null
mkdir -p "$DEST"
cp -a "$ROOT/." "$DEST/"
# Nunca incluir credenciais, diretórios privados ou arquivos de trabalho.
find "$DEST" -type d -name '__pycache__' -prune -exec rm -rf {} +
find "$DEST" -type f \( -name '*.pyc' -o -name '*.sagaz' \) -delete
git add -- "$DEST"
echo '[SagaZ] Arquivos preparados:'
git diff --cached --stat
echo
read -r -p "Digite PUBLICAR para criar commit e enviar a branch ao GitHub: " confirm
if [ "$confirm" != 'PUBLICAR' ]; then echo 'Cancelado; repositório remoto inalterado.'; exit 0; fi
git -c user.name="$(git config user.name || echo dSant)" -c user.email="$(git config user.email || echo noreply@users.noreply.github.com)" commit -m 'feat: blue matrix HooLeeSh33t e dSanT-CreaTor isolados' >/dev/null
if git push -u origin "$BRANCH"; then
  echo "[OK] Abra: https://github.com/21daTitan/SagaZ-ZeRo/pull/new/$BRANCH"
else
  echo '[FALHA] GitHub não aceitou o push. Faça gh auth login e tente novamente.'
  exit 1
fi
