# ⬡ SagaZ — persona azul, carioca desenrolado (HooLeeSh33t v0.1)
# Mesmo executor que zero.ps1 e que agent.py puro — só muda a roupa.
# Arquivo NOVO, não toca em nada já resolvido.

$Dir = Split-Path -Parent $PSScriptRoot
python "$Dir\sagaz_zero\persona_launcher.py" --as sagaz $args
