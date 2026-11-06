"""Capability negotiation cache with bounded TTL and identity separation."""
from dataclasses import dataclass
import threading
import time
from typing import Callable


@dataclass(frozen=True)
class Capability:
    connector: str
    model: str
    tools: bool = False
    streaming: bool = False
    images: bool = False
    source: str = "local_manifest"


class CapabilityCache:
    def __init__(self, ttl_seconds: float = 60.0, clock: Callable = time.monotonic):
        if not 1 <= ttl_seconds <= 3600:
            raise ValueError("Invalid TTL")
        self.ttl = ttl_seconds
        self.clock = clock
        self._entries = {}
        self._lock = threading.RLock()

    def get_or_load(self, connector: str, model: str, loader: Callable[[], Capability]):
        key = (connector, model)
        now = self.clock()
        with self._lock:
            item = self._entries.get(key)
            if item and item[0] > now:
                return item[1]
            result = loader()
            if not isinstance(result, Capability) or result.connector != connector or result.model != model:
                raise ValueError("Invalid capability declaration")
            self._entries[key] = (self.clock() + self.ttl, result)
            return result

    def invalidate(self, connector: str | None = None):
        with self._lock:
            if connector is None:
                self._entries.clear()
            else:
                for key in tuple(self._entries):
                    if key[0] == connector:
                        del self._entries[key]
