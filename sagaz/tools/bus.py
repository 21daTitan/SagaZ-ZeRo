"""Policy-checked tool dispatch with independent audit trail."""
from sagaz.gateway.policy import Denied
from sagaz.tools.builtin import BUILTINS

class Bus:
    def __init__(self, audit=None):
        self.audit = audit

    def names(self, scope):
        return sorted(name for name in BUILTINS if name in scope.tools)

    def call(self, scope, name, arguments=None):
        scope.check_tool(name)
        if name not in BUILTINS:
            raise Denied('Unknown or disabled tool')
        if arguments not in ({}, None):
            raise ValueError('No arguments accepted for this tool')
        result = BUILTINS[name]()
        if self.audit:
            self.audit.append('tool_call', {'name': name, 'connector': scope.connector})
        return result
