#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SagaZ-ZeRo — Persona Launcher (HooLeeSh33t v0.1)
---------------------------------------------------
Arquivo NOVO e 100% ADITIVO.

Este launcher NÃO importa agent.py como módulo e NÃO altera uma
linha dele. Ele apenas abre agent.py como um PROCESSO FILHO (via
pty no Linux/macOS/Termux, ou subprocess puro no Windows) e observa
o texto que já sai na tela, desenhando um banner de persona por
cima quando reconhece um gatilho (ver persona_display.py).

Se este arquivo for deletado, agent.py continua funcionando 100%
normal e sem nenhuma diferença — prova de que é puramente aditivo.

Uso:
  python3 sagaz_zero/persona_launcher.py --as sagaz [args do agent.py]
  python3 sagaz_zero/persona_launcher.py --as zero  [args do agent.py]

Variável de ambiente opcional:
  SAGAZ_ZERO_PERSONA_MODE = action | command | dual   (padrão: command)
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

# Import relativo simples — este arquivo vive dentro do pacote
# sagaz_zero/, então funciona tanto chamado direto quanto via -m.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from persona_display import PersonaMode, format_persona_banner, startup_banner  # noqa: E402

try:
    import pty  # POSIX only (Linux, macOS, Termux)
    HAS_PTY = True
except ImportError:
    HAS_PTY = False


REPO_ROOT = Path(__file__).resolve().parent.parent
AGENT_PY = REPO_ROOT / "agent.py"


def _resolve_python() -> str:
    """Usa o mesmo interpretador que está rodando este launcher."""
    return sys.executable or "python3"


def _spawn_with_pty(argv: list[str], mode: PersonaMode, invoked_as: str) -> int:
    """
    Caminho POSIX (Linux/macOS/Termux). Usa pty pra que agent.py
    continue pensando que está num terminal real (mantém as cores
    e o comportamento interativo dele intactos).
    """
    buffer = b""

    def master_read(fd: int) -> bytes:
        nonlocal buffer
        data = os.read(fd, 1024)
        if not data:
            return data

        buffer += data
        text = buffer.decode("utf-8", errors="ignore")
        parts = text.split("\n")

        if not text.endswith("\n"):
            # última parte é uma linha incompleta: guarda pra próxima leitura
            complete_lines, leftover = parts[:-1], parts[-1]
            buffer = leftover.encode("utf-8", errors="ignore")
        else:
            complete_lines, buffer = [p for p in parts if p != "" or True][:-1], b""

        for line in complete_lines:
            banner = format_persona_banner(mode, invoked_as, line)
            if banner:
                os.write(1, (banner + "\n").encode("utf-8", errors="ignore"))

        return data

    return pty.spawn(argv, master_read) or 0


def _spawn_with_subprocess(argv: list[str], mode: PersonaMode, invoked_as: str) -> int:
    """
    Caminho de fallback (Windows, ou qualquer SO sem módulo pty).
    Sem pseudo-terminal: funcional, mas as cores nativas de
    agent.py podem ficar desativadas se ele detectar que não é
    um tty real. O banner de persona aparece do mesmo jeito.
    """
    env = dict(os.environ)
    env.setdefault("FORCE_COLOR", "1")  # pede pra manter cor, best-effort

    proc = subprocess.Popen(
        argv,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        stdin=sys.stdin,
        text=True,
        bufsize=1,
        env=env,
    )
    assert proc.stdout is not None
    for raw_line in proc.stdout:
        line = raw_line.rstrip("\n")
        banner = format_persona_banner(mode, invoked_as, line)
        if banner:
            print(banner)
        print(raw_line, end="")
    proc.wait()
    return proc.returncode or 0


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="sagaz / zero",
        description="SagaZ-ZeRo com persona visual (HooLeeSh33t v0.1)",
        add_help=False,  # repassa --help pro agent.py também
    )
    parser.add_argument("--as", dest="invoked_as", choices=["sagaz", "zero"], default=None)
    parser.add_argument(
        "--persona-mode",
        dest="persona_mode",
        choices=[m.value for m in PersonaMode],
        default=None,
    )
    args, remaining = parser.parse_known_args()

    invoked_as = args.invoked_as
    if not invoked_as:
        # Se não veio explícito, deduz pelo nome do programa chamado
        prog_name = Path(sys.argv[0]).stem.lower()
        invoked_as = "zero" if "zero" in prog_name else "sagaz"

    mode = PersonaMode.from_str(args.persona_mode or os.environ.get("SAGAZ_ZERO_PERSONA_MODE"))

    if not AGENT_PY.exists():
        print(f"[persona] agent.py não encontrado em {AGENT_PY}", file=sys.stderr)
        return 1

    print(startup_banner(mode, invoked_as))

    target = [_resolve_python(), str(AGENT_PY), *remaining]

    if HAS_PTY and os.name == "posix":
        return _spawn_with_pty(target, mode, invoked_as)
    else:
        return _spawn_with_subprocess(target, mode, invoked_as)


if __name__ == "__main__":
    sys.exit(main())
