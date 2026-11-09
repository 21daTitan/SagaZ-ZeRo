# ⬡ SagaZ-ZeRo — HooLeeSh33t EdiTioN by dSanT
# Launcher Windows PowerShell
# Base: Evil Cassandra por Mörlsara

param(
  [string]$Mode = "",
  [int]$Port = 8080
)

Set-Location $PSScriptRoot

if (Test-Path ".venv\Scripts\Activate.ps1") {
  & .venv\Scripts\Activate.ps1
} elseif (Test-Path "venv\Scripts\Activate.ps1") {
  & venv\Scripts\Activate.ps1
}

if ($Mode -eq "web") {
  Write-Host ""
  Write-Host "⬡ SagaZ-ZeRo · HooLeeSh33t EdiTioN"
  Write-Host "  Interface Web em http://localhost:$Port"
  Write-Host ""
  python web_ui.py --port $Port
} else {
  Write-Host ""
  Write-Host "⬡ SagaZ-ZeRo · HooLeeSh33t EdiTioN · CLI"
  Write-Host ""
  python agent.py $args
}
