@echo off
REM ⬡ SagaZ-ZeRo — HooLeeSh33t EdiTioN by dSanT
REM Launcher Windows CMD
REM Base: Evil Cassandra por Mörlsara

cd /d "%~dp0"

if exist .venv\Scripts\activate.bat (
  call .venv\Scripts\activate.bat
) else if exist venv\Scripts\activate.bat (
  call venv\Scripts\activate.bat
)

if "%1"=="web" (
  set PORT=%2
  if "%PORT%"=="" set PORT=8080
  echo.
  echo ⬡ SagaZ-ZeRo · HooLeeSh33t EdiTioN
  echo   Interface Web em http://localhost:%PORT%
  echo.
  python web_ui.py --port %PORT%
) else (
  echo.
  echo ⬡ SagaZ-ZeRo · HooLeeSh33t EdiTioN · CLI
  echo.
  python agent.py %*
)
