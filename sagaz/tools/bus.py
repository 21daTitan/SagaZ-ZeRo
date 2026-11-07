"""Policy-checked tool dispatch with independent audit trail."""
from sagaz.gateway.policy import Denied
from sagaz.tools.builtin import BUILTINS

class Bus:
    def __init__(self, audit=None, db_path=None):
        self.audit = audit
        self.db_path = db_path

    def names(self, scope):
        return sorted(name for name in BUILTINS if name in scope.tools)

    def call(self, scope, name, arguments=None):
        scope.check_tool(name)
        if name not in BUILTINS:
            raise Denied('Unknown or disabled tool')
        if name == 'sagaz_cti_search':
            if not isinstance(arguments, dict) or set(arguments) - {'query', 'limit'}:
                raise ValueError('Invalid CTI search arguments')
            result = BUILTINS[name](arguments.get('query'), arguments.get('limit', 10))
        elif name == 'sagaz_discord_search':
            if not isinstance(arguments, dict) or set(arguments) - {'query', 'limit'}:
                raise ValueError('Invalid Discord search arguments')
            from sagaz.discord_memory import DiscordMemory
            result = DiscordMemory(self.db_path or 'projects/sagaz/discord_memory.sqlite3').search(arguments.get('query'), arguments.get('limit', 20))
        elif name == 'sagaz_discord_summary':
            if arguments not in ({}, None):
                raise ValueError('No arguments accepted for this tool')
            from sagaz.discord_memory import DiscordMemory
            result = DiscordMemory(self.db_path or 'projects/sagaz/discord_memory.sqlite3').summary()
        else:
            if arguments not in ({}, None):
                raise ValueError('No arguments accepted for this tool')
            result = BUILTINS[name]()
        if self.audit:
            self.audit.append('tool_call', {'name': name, 'connector': scope.connector})
        return result
