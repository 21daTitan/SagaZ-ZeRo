"""Sistema de plugins do agente.

Um plugin vive em ``<raiz>/plugins/<nome>/plugin.json`` e **registra ferramentas**.
Manifesto:

```json
{
  "name": "exemplo",
  "version": "1.0.0",
  "scopes": ["fs.read"],
  "tools": [
    {"name": "exemplo_ola", "description": "...", "scope": "fs.read",
     "parameters": {"type": "object", "properties": {}, "required": []},
     "entry": "handlers.py:ola"}
  ]
}
```

Segurança:
- cada ferramenta só pode pedir um escopo **declarado** em ``scopes`` do plugin;
- o plugin só é carregado se estiver **habilitado** (aprovado) pelo operador;
- carregar um plugin executa código Python dele — por isso exige habilitação
  explícita; para plugins de terceiros, rode em sandbox (ver docs/ROADMAP.md).
"""
from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

from sagaz.agent.core import SCOPES, AgentError
from sagaz.agent.registry import Registry, ToolSpec

_NAME = re.compile(r'^[a-z0-9][a-z0-9_-]{0,48}$')


class PluginError(AgentError):
    pass


def load_manifest(path: Path) -> dict:
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    if not isinstance(data, dict):
        raise PluginError('manifesto deve ser um objeto JSON')
    name = data.get('name', '')
    if not isinstance(name, str) or not _NAME.match(name):
        raise PluginError(f'nome de plugin inválido: {name!r}')
    scopes = data.get('scopes', [])
    if not isinstance(scopes, list) or set(scopes) - SCOPES:
        raise PluginError('scopes inválidos no manifesto')
    tools = data.get('tools', [])
    if not isinstance(tools, list) or not tools:
        raise PluginError('o plugin precisa declarar ao menos uma ferramenta')
    for tool in tools:
        if not isinstance(tool, dict):
            raise PluginError('ferramenta inválida')
        for field in ('name', 'scope', 'entry'):
            if not isinstance(tool.get(field), str) or not tool[field]:
                raise PluginError(f'ferramenta sem campo {field}')
        if tool['scope'] not in set(scopes):
            raise PluginError(f"ferramenta {tool['name']} pede escopo não declarado: {tool['scope']}")
        if ':' not in tool['entry']:
            raise PluginError("entry deve ser 'arquivo.py:funcao'")
        rel = tool['entry'].split(':', 1)[0]
        if rel.startswith(('/', '.')) or '..' in Path(rel).parts:
            raise PluginError(f'entry fora do plugin: {rel}')
    data.setdefault('version', '0.0.0')
    return data


class PluginManager:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.dir = self.root / 'plugins'
        self.enabled_file = self.dir / 'enabled.json'

    def _enabled_names(self) -> set[str]:
        try:
            data = json.loads(self.enabled_file.read_text(encoding='utf-8'))
            return set(data) if isinstance(data, list) else set()
        except (OSError, ValueError):
            return set()

    def _write_enabled(self, names) -> None:
        self.dir.mkdir(parents=True, exist_ok=True)
        self.enabled_file.write_text(json.dumps(sorted(names), ensure_ascii=False, indent=2), encoding='utf-8')

    def discover(self) -> list[dict]:
        found = []
        if not self.dir.is_dir():
            return found
        for manifest in sorted(self.dir.glob('*/plugin.json')):
            if manifest.is_symlink():
                continue
            try:
                data = load_manifest(manifest)
            except PluginError:
                continue
            data['_dir'] = str(manifest.parent)   # diretório real (pode diferir do nome)
            found.append(data)
        return found

    def list(self) -> list[dict]:
        enabled = self._enabled_names()
        return [{'name': m['name'], 'version': m['version'], 'scopes': m.get('scopes', []),
                 'tools': [t['name'] for t in m['tools']], 'enabled': m['name'] in enabled}
                for m in self.discover()]

    def enable(self, name: str) -> dict:
        available = {m['name'] for m in self.discover()}
        if name not in available:
            raise PluginError(f'plugin não encontrado: {name}')
        names = self._enabled_names() | {name}
        self._write_enabled(names)
        return {'enabled': sorted(names)}

    def disable(self, name: str) -> dict:
        names = self._enabled_names() - {name}
        self._write_enabled(names)
        return {'enabled': sorted(names)}

    def load_into(self, registry: Registry) -> list[str]:
        """Carrega as ferramentas dos plugins habilitados no registro. Retorna os nomes carregados."""
        enabled = self._enabled_names()
        loaded = []
        for manifest in self.discover():
            if manifest['name'] not in enabled:
                continue
            plugin_dir = Path(manifest['_dir'])
            for tool in manifest['tools']:
                rel, func_name = tool['entry'].split(':', 1)
                module = self._import(plugin_dir, manifest['name'], rel)
                handler = getattr(module, func_name, None)
                if not callable(handler):
                    raise PluginError(f"handler ausente: {tool['entry']}")
                registry.register(ToolSpec(
                    name=tool['name'],
                    description=tool.get('description', manifest['name']),
                    scope=tool['scope'],
                    parameters=tool.get('parameters', {'type': 'object', 'properties': {}, 'required': []}),
                    handler=handler,
                ))
                loaded.append(tool['name'])
        return loaded

    @staticmethod
    def _import(plugin_dir: Path, plugin_name: str, rel: str):
        file = (plugin_dir / rel).resolve()
        if plugin_dir.resolve() not in file.parents:
            raise PluginError(f'entry fora do plugin: {rel}')
        spec = importlib.util.spec_from_file_location(f'sagaz_plugin_{plugin_name}_{file.stem}', file)
        if spec is None or spec.loader is None:
            raise PluginError(f'não foi possível carregar {rel}')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module


__all__ = ['PluginManager', 'PluginError', 'load_manifest']
