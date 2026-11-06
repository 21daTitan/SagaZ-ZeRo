#!/usr/bin/env bash
# Explicit opt-in helper: clones GitHub and creates a new branch; never overwrites remote files.
set -euo pipefail
if [[ $# -ne 2 ]]; then
  echo "Usage: $0 /path/to/SagaZ-ZeRo-v3.7.0-zeRo.zip https://github.com/21daTitan/SagaZ-ZeRo.git" >&2
  exit 2
fi
archive=$(realpath "$1")
repository="$2"
case "$repository" in
  https://github.com/21daTitan/SagaZ-ZeRo|https://github.com/21daTitan/SagaZ-ZeRo.git) ;;
  *) echo 'Unsupported destination. Confirm the owner/repository URL.' >&2; exit 2;;
esac
command -v git >/dev/null || { echo 'Install git first'; exit 1; }
command -v python3 >/dev/null || { echo 'Install Python 3 first'; exit 1; }
workdir=$(mktemp -d)
trap 'rm -rf "$workdir"' EXIT
# Git credential manager / gh login must already be configured by the user.
git clone "$repository" "$workdir/repository"
cd "$workdir/repository"
branch="sagaz-v3.7.0-$(date +%Y%m%d%H%M%S)"
git switch -c "$branch"
python3 "$(dirname "$(realpath "$0")")/safe_merge.py" "$archive" "$PWD" --apply > "$workdir/merge-report.json"
cat "$workdir/merge-report.json"
if [[ -z "$(git status --porcelain)" ]]; then
  echo 'No new files; there may be conflicts that require review. Nothing pushed.'
  exit 0
fi
git add -A
git commit -m 'feat: add verified SagaZ ZeRo v3.7.0 components without overwriting upstream'
git push -u origin "$branch"
echo "Branch created: $branch. Review and open a PR before merging."
