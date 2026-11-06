"""Authenticated request identities, scoped tools, per-connector rate limits."""
from dataclasses import dataclass
import secrets
import threading
import time


class Denied(PermissionError):
    pass


@dataclass(frozen=True)
class Scope:
    connector: str
    tools: frozenset[str]
    dial: int = 2
    budget_usd: float = 0.0
    fs_roots: tuple[str, ...] = ()
    shell: bool = False

    def check_tool(self, name: str):
        if name not in self.tools:
            raise Denied(f"Tool '{name}' not permitted for connector '{self.connector}'")


PUBLIC = Scope("public", frozenset())
LOCAL_UI = Scope("local-ui", frozenset({"sagaz_status", "sagaz_skills"}))
TOKEN_API = Scope("token-api", frozenset({"sagaz_status", "sagaz_skills"}))


class RateLimiter:
    """Fixed-window per-identity quota, not a global shared limiter."""
    def __init__(self, limits: dict[str, tuple[int, float]] | None = None, clock=time.monotonic):
        self.limits = limits or {"local-ui": (120, 60.0), "token-api": (60, 60.0), "public": (10, 60.0)}
        self.clock = clock
        self._events = {}
        self._lock = threading.Lock()

    def allow(self, identity: str) -> bool:
        amount, window = self.limits.get(identity, (20, 60.0))
        now = self.clock()
        with self._lock:
            history = [ts for ts in self._events.get(identity, []) if now - ts < window]
            if len(history) >= amount:
                self._events[identity] = history
                return False
            history.append(now)
            self._events[identity] = history
            return True


def authenticate(cookie: str | None, session: str, bearer: str | None, api_token: str | None):
    # A connector cannot grant itself scopes using X-Connector or any other untrusted header.
    if cookie and secrets.compare_digest(cookie, session):
        return LOCAL_UI
    if api_token and bearer and secrets.compare_digest(bearer, api_token):
        return TOKEN_API
    return PUBLIC
