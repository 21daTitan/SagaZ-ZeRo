#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SagaZ-ZeRo — Persona Display Engine (HooLeeSh33t v0.1)
--------------------------------------------------------
Módulo NOVO e 100% ADITIVO. Não importa nem modifica nada de
agent.py, web_ui.py ou cassandra/ — apenas observa texto já
impresso por eles (via persona_launcher.py) e decide se/como
desenhar um "crachá" colorido por cima.

Mesmo executor, duas caras:

  ⬡ SagaZ  — azul, carioca desenrolado, descontraído. "O Abusado."
  ⬢ ZeRo   — vermelho/branco, direto ao ponto, sangue frio.

NÃO é uma segunda IA. É a MESMA IA (agent.py / cassandra/) com um
rótulo visual diferente dependendo do modo escolhido.

═══════════════════════════════════════════════════════════════
REGRA DE OURO PRA QUEM FOR MEXER AQUI DEPOIS:
═══════════════════════════════════════════════════════════════
Existem 3 MODOS de exibição, e eles são INDEPENDENTES entre si.
Cada modo tem sua própria função de renderização (_render_mode_*).
NENHUMA dessas funções chama a outra, lê estado da outra, ou
depende de qualquer variável global mutável compartilhada.

   • Isso é de propósito. É pra garantir que ativar/trocar um modo
     NUNCA corrompe, atropela ou embaralha o comportamento de outro.
   • Se você for adicionar um modo novo, siga o padrão: uma função
     pura, isolada, que recebe os dados que precisa como argumento
     e retorna uma string — sem mexer nas outras.
   • "Ordem e Progresso." — não misture.
═══════════════════════════════════════════════════════════════
"""

from __future__ import annotations

from enum import Enum
from typing import Optional


# ─────────────────────────────────────────────────────────────
# CORES — ANSI puro, sem depender da classe ANSI de agent.py
# (propositalmente desacoplado: este módulo nunca importa agent.py)
# ─────────────────────────────────────────────────────────────
class _C:
    RESET = "\033[0m"
    BOLD = "\033[1m"

    # SagaZ — azul carioca, descontraído
    SAGAZ_BLUE = "\033[1;94m"      # azul brilhante em negrito
    SAGAZ_GLYPH = "⬡"

    # ZeRo — vermelho/branco, sangue frio
    ZERO_WHITE = "\033[1;97m"      # branco brilhante em negrito
    ZERO_RED = "\033[1;91m"        # vermelho brilhante (moldura/acento)
    ZERO_GLYPH = "⬢"


class PersonaMode(str, Enum):
    """Os 3 modos oficiais. Veja a regra de ouro no topo do arquivo."""
    ACTION = "action"      # troca a persona conforme o TIPO de ação
    COMMAND = "command"    # persona fixa conforme o COMANDO digitado (sagaz/zero)
    DUAL = "dual"          # mostra as DUAS personas sempre, empilhadas

    @classmethod
    def from_str(cls, value: Optional[str]) -> "PersonaMode":
        if not value:
            return cls.COMMAND
        value = value.strip().lower()
        for mode in cls:
            if mode.value == value:
                return mode
        # Valor desconhecido: cai pro padrão em vez de quebrar a execução.
        return cls.COMMAND


# ─────────────────────────────────────────────────────────────
# CLASSIFICAÇÃO DE AÇÃO
# ─────────────────────────────────────────────────────────────
# Estas strings batem com textos que JÁ existem na saída visível de
# agent.py (não precisamos alterá-lo: só reconhecemos o que ele já
# imprime). Se o texto de agent.py mudar no futuro, só ajuste as
# listas abaixo — nenhuma outra parte do código precisa mudar.

_THINK_MARKERS = (
    "está processando",
    "buscando na web autonomamente",
    "RESULTADOS DA BUSCA NA WEB",
    "Interface SagaZ-ZeRo inicializada",
    "digitar outro prompt",
)

_EXEC_MARKERS = (
    "solicitou ferramenta",
    "solicitou a skill",
    "pausado por proteção",
    "Prompt enviado ao SagaZ-ZeRo",
    "Encerrando o SagaZ-ZeRo",
    "Erro ao consultar",
)


def classify_action(line: str) -> Optional[str]:
    """
    Decide se uma linha de saída representa:
      - "think" (raciocínio/conversa/busca) → papel do SagaZ
      - "exec"  (execução direta/ferramenta/comando) → papel do ZeRo
      - None    (linha comum, sem gatilho — não desenha banner nenhum)

    Função pura. Não modifica nada, não guarda estado.
    """
    if not line:
        return None
    for marker in _EXEC_MARKERS:
        if marker in line:
            return "exec"
    for marker in _THINK_MARKERS:
        if marker in line:
            return "think"
    return None


# ─────────────────────────────────────────────────────────────
# MODO 1 — ACTION: a persona troca conforme o TIPO de ação
# ─────────────────────────────────────────────────────────────
def _render_mode_action(kind: str) -> str:
    """
    kind já vem de classify_action(): "think" ou "exec".
    Isolado: só olha pro 'kind', não sabe nem precisa saber
    qual comando foi digitado.
    """
    if kind == "exec":
        return (
            f"{_C.ZERO_RED}{_C.ZERO_GLYPH}{_C.RESET} "
            f"{_C.ZERO_WHITE}ZeRo{_C.RESET} "
            f"{_C.ZERO_RED}· sangue frio · executando{_C.RESET}"
        )
    # default/"think"
    return (
        f"{_C.SAGAZ_BLUE}{_C.SAGAZ_GLYPH}{_C.RESET} "
        f"{_C.SAGAZ_BLUE}SagaZ{_C.RESET} "
        f"{_C.SAGAZ_BLUE}· abusado · pensando{_C.RESET}"
    )


# ─────────────────────────────────────────────────────────────
# MODO 2 — COMMAND: a persona é fixa pelo comando digitado
# ─────────────────────────────────────────────────────────────
def _render_mode_command(invoked_as: str) -> str:
    """
    invoked_as vem de qual comando o usuário chamou: 'sagaz' ou 'zero'.
    Isolado: não olha pro tipo de ação (kind) de forma alguma —
    a persona nunca muda dentro da mesma sessão de comando.
    """
    if invoked_as == "zero":
        return (
            f"{_C.ZERO_RED}{_C.ZERO_GLYPH}{_C.RESET} "
            f"{_C.ZERO_WHITE}ZeRo{_C.RESET} "
            f"{_C.ZERO_RED}· sangue frio{_C.RESET}"
        )
    # default: sagaz
    return (
        f"{_C.SAGAZ_BLUE}{_C.SAGAZ_GLYPH}{_C.RESET} "
        f"{_C.SAGAZ_BLUE}SagaZ{_C.RESET} "
        f"{_C.SAGAZ_BLUE}· abusado{_C.RESET}"
    )


# ─────────────────────────────────────────────────────────────
# MODO 3 — DUAL: as duas personas sempre, uma embaixo da outra
# ─────────────────────────────────────────────────────────────
def _render_mode_dual() -> str:
    """
    Isolado: não olha pro kind nem pro invoked_as. Sempre as duas,
    sempre na mesma ordem (SagaZ em cima, ZeRo embaixo).
    """
    linha_sagaz = (
        f"{_C.SAGAZ_BLUE}{_C.SAGAZ_GLYPH} SagaZ{_C.RESET} "
        f"{_C.SAGAZ_BLUE}· abusado{_C.RESET}"
    )
    linha_zero = (
        f"{_C.ZERO_RED}{_C.ZERO_GLYPH}{_C.RESET} "
        f"{_C.ZERO_WHITE}ZeRo{_C.RESET} "
        f"{_C.ZERO_RED}· sangue frio{_C.RESET}"
    )
    return f"{linha_sagaz}\n{linha_zero}"


# ─────────────────────────────────────────────────────────────
# DISPATCHER — ponto único de entrada. Nunca mistura os modos.
# ─────────────────────────────────────────────────────────────
def format_persona_banner(
    mode: PersonaMode,
    invoked_as: str,
    line: str,
) -> Optional[str]:
    """
    Retorna o banner de persona pra uma linha de saída, ou None se
    a linha não for um gatilho reconhecido (sem banner = sem poluir
    a tela com rótulo em cada linha de texto comum).

    O 'if/elif' abaixo é proposital: cada ramo chama EXATAMENTE uma
    função de renderização e nenhuma outra. Não combine, não
    encadeie, não deixe um modo "ler" o resultado do outro.
    """
    kind = classify_action(line)
    if kind is None:
        return None

    if mode == PersonaMode.ACTION:
        return _render_mode_action(kind)
    elif mode == PersonaMode.COMMAND:
        return _render_mode_command(invoked_as)
    elif mode == PersonaMode.DUAL:
        return _render_mode_dual()

    # Nunca deve chegar aqui (PersonaMode.from_str já normaliza),
    # mas se chegar, falha de forma visível em vez de silenciosa.
    raise ValueError(f"Modo de persona não implementado: {mode!r}")


def startup_banner(mode: PersonaMode, invoked_as: str) -> str:
    """Banner de abertura mostrado uma vez, ao iniciar a sessão."""
    label = "SagaZ" if invoked_as != "zero" else "ZeRo"
    color = _C.SAGAZ_BLUE if invoked_as != "zero" else _C.ZERO_WHITE
    return (
        f"\n{color}{_C.BOLD}"
        f"╭─────────────────────────────────────────────╮\n"
        f"│  ⬡⬢  SagaZ-ZeRo · HooLeeSh33t EdiTioN v0.1   │\n"
        f"│  Persona ativa: {label:<10} · Modo: {mode.value:<8} │\n"
        f"╰─────────────────────────────────────────────╯"
        f"{_C.RESET}\n"
    )
