@echo off
REM ⬡ SagaZ — persona azul, carioca desenrolado (HooLeeSh33t v0.1)
REM Mesmo executor que zero.bat e que agent.py puro — só muda a roupa.
REM Arquivo NOVO, não toca em nada já resolvido.

set DIR=%~dp0..
python "%DIR%\sagaz_zero\persona_launcher.py" --as sagaz %*
