"""Named connector profiles; no external CLI automatically installed or configured."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Connector:
    name: str
    protocol: str = 'MCP JSON-RPC (local HTTP only)'
    installed: bool = False
    authenticated: bool = False
    note: str = 'Explicit setup and credentials required'
