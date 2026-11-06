"""Compat alias for the embedded HTTP gateway in sagaz.app."""
from sagaz.app import Handler, Server, serve

__all__ = ('Handler', 'Server', 'serve')
