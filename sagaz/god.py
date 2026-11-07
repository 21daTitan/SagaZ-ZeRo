"""Resolved SagaZ operating profiles.

The profile changes context and autonomy hints only.  It never disables the
destructive-command confirmation boundary.
"""
from dataclasses import dataclass
import os
import re
from typing import Literal


@dataclass(frozen=True)
class GodProfile:
    name: str
    sanitize: bool
    guard_mode: Literal["rewrite", "assertive"]
    max_iterations: int
    skill_char_limit: int
    auto_shell: bool
    confirm_destructive: bool
    temperature: float
    context_window: int


DEVOTIONAL = GodProfile("devocional", True, "rewrite", 8, 6000, False, True, 0.70, 8000)
DEUS = GodProfile("deus", False, "assertive", 40, 0, True, True, 0.95, 200000)


def resolve(level: str | None = None, env: str | None = None) -> GodProfile:
    """Resolve explicit level first, then ``SAGAZ_GOD_MODE``."""
    value = (level if level is not None else env if env is not None else os.environ.get("SAGAZ_GOD_MODE", ""))
    return DEUS if str(value).strip().lower() in {"deus", "god", "1", "on", "max", "true"} else DEVOTIONAL


def is_destructive_command(command: str) -> bool:
    """Conservative check used before any shell executor is added."""
    if not isinstance(command, str):
        return True
    text = command.lower().strip()
    patterns = (
        r"\brm\s+-[a-z]*r", r"git\s+(?:reset\s+--hard|clean\s+-fd)",
        r"\bdd\s+", r"\bmkfs(?:\.|\s)", r"docker\s+system\s+prune",
        r"\bdrop\s+table", r">\s*/dev/", r"chmod\s+-r", r"\b(?:fdisk|pvremove|lvremove)\b",
        r"\b(?:pip|npm)\s+uninstall\b",
    )
    return any(re.search(pattern, text) for pattern in patterns) or any(
        marker in text for marker in ("sudo ", "doas ", "pkexec ", "su -c")
    )


def system_prompt(profile: GodProfile | None = None) -> str:
    """Small, provider-neutral operating layer for chat completions."""
    profile = profile or resolve()
    return (
        f"Você é SagaZ-ZeRo, operador HooLeeSh33t. Perfil: {profile.name}. "
        "Execute diagnóstico incremental, declare incerteza e não invente resultados. "
        "Leia a saída antes de seguir. Ações destrutivas sempre exigem confirmação explícita."
    )


def public_dict(profile: GodProfile | None = None) -> dict:
    profile = profile or resolve()
    return {"name": profile.name, "guard_mode": profile.guard_mode,
            "max_iterations": profile.max_iterations, "skill_char_limit": profile.skill_char_limit,
            "auto_shell": profile.auto_shell, "confirm_destructive": profile.confirm_destructive,
            "temperature": profile.temperature, "context_window": profile.context_window}
