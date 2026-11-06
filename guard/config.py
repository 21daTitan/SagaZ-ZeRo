"""Explicit, visible and disabled-by-default GUARD workload settings."""
from dataclasses import dataclass
import os

@dataclass(frozen=True)
class GuardConfig:
    enabled: bool = False
    cpu_quota_pct: int = 15
    memory_max_mb: int = 280
    service_name: str = "sagaz-guard-opt-in"


def load():
    enabled = os.environ.get('SAGAZ_GUARD_ENABLED') == '1'
    return GuardConfig(enabled=enabled)
