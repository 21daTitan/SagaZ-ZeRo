@echo off
REM ⬡⬢ SagaZ-ZeRo — Instalador desktop (Windows CMD)
REM HooLeeSh33t v0.1 — arquivo NOVO, não toca nos launchers já resolvidos.

cd /d "%~dp0"

echo.
echo ⬡⬢ SagaZ-ZeRo — instalador desktop
echo    Base: Evil Cassandra — Morlsara Code Nexus
echo.

where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
  echo Python nao encontrado. Instale Python 3.10+ antes de continuar.
  exit /b 1
)

echo Criando ambiente virtual (.venv)...
python -m venv .venv
call .venv\Scripts\activate.bat

echo Atualizando pip...
pip install --upgrade pip -q

if "%1"=="--cli-only" (
  echo Modo CLI-only: instalando so o essencial...
  pip install httpx requests python-dotenv cryptography
) else (
  echo Instalando todas as dependencias ^(CLI + Web^)...
  pip install -r requirements.txt
)

echo.
echo Instalado! Pra usar:
echo    .venv\Scripts\activate.bat
echo    sagaz-zero.bat web          ^(interface web Matrix^)
echo    bin\sagaz.bat               ^(CLI persona azul - SagaZ^)
echo    bin\zero.bat                ^(CLI persona vermelha/branca - ZeRo^)
echo.
