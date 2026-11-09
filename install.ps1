# ⬡⬢ SagaZ-ZeRo — Instalador desktop (Windows PowerShell)
# HooLeeSh33t v0.1 — arquivo NOVO, não toca nos launchers já resolvidos.

param(
  [switch]$CliOnly
)

Set-Location $PSScriptRoot

Write-Host ""
Write-Host "⬡⬢ SagaZ-ZeRo — instalador desktop"
Write-Host "   Base: Evil Cassandra — Mörlsara Code Nexus"
Write-Host ""

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
  Write-Host "✗ Python não encontrado. Instale Python 3.10+ antes de continuar."
  exit 1
}

Write-Host "→ Criando ambiente virtual (.venv)..."
python -m venv .venv
& .venv\Scripts\Activate.ps1

Write-Host "→ Atualizando pip..."
pip install --upgrade pip -q

if ($CliOnly) {
  Write-Host "→ Modo CLI-only: instalando só o essencial..."
  pip install httpx requests python-dotenv cryptography
} else {
  Write-Host "→ Instalando todas as dependências (CLI + Web)..."
  pip install -r requirements.txt
}

Write-Host ""
Write-Host "✅ Instalado! Pra usar:"
Write-Host "   .venv\Scripts\Activate.ps1"
Write-Host "   .\sagaz-zero.ps1 web         # interface web Matrix"
Write-Host "   .\bin\sagaz.ps1              # CLI persona azul (SagaZ)"
Write-Host "   .\bin\zero.ps1               # CLI persona vermelha/branca (ZeRo)"
Write-Host ""
