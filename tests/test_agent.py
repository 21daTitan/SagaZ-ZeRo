"""Testes do subsistema de agente de código (segurança + ferramentas + loop)."""
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from sagaz.agent.core import (AgentPolicy, ConfirmationRequired, PathEscape, READ_ONLY,
                              ScopeDenied, resolve_in_root)
from sagaz.agent.fs_tools import FsTools
from sagaz.agent.exec_tools import ExecTools
from sagaz.agent.git_tools import GitTools, _reject_force
from sagaz.agent.registry import Registry, register_builtin
from sagaz.agent.plugins import PluginManager, PluginError, load_manifest
from sagaz.agent.loop import AgentLoop
from sagaz.agent.core import AgentError


def _writable(auto=True):
    return AgentPolicy(READ_ONLY | {'fs.write', 'exec', 'git.write'}, auto_confirm=auto)


class ConfinementTests(unittest.TestCase):
    def test_blocks_traversal_and_absolute(self):
        with tempfile.TemporaryDirectory() as tmp:
            for bad in ('../outside', '/etc/passwd', '', '  '):
                with self.assertRaises(PathEscape):
                    resolve_in_root(tmp, bad)

    def test_blocks_symlink_escape(self):
        with tempfile.TemporaryDirectory() as tmp:
            link = Path(tmp) / 'escape'
            link.symlink_to('/etc')
            with self.assertRaises(PathEscape):
                resolve_in_root(tmp, 'escape/passwd')

    def test_allows_inside(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / 'a').mkdir()
            self.assertEqual(resolve_in_root(tmp, 'a'), (Path(tmp) / 'a').resolve())


class PolicyTests(unittest.TestCase):
    def test_scope_gating(self):
        p = AgentPolicy(READ_ONLY)
        p.require('fs.read')
        with self.assertRaises(ScopeDenied):
            p.require('fs.write')

    def test_confirmation(self):
        with self.assertRaises(ConfirmationRequired):
            AgentPolicy({'fs.write'}, confirm=lambda a: False).confirm('x')
        AgentPolicy({'fs.write'}, auto_confirm=True).confirm('x')  # não levanta


class FsToolsTests(unittest.TestCase):
    def test_read_write_edit_with_backup(self):
        with tempfile.TemporaryDirectory() as tmp:
            fs = FsTools(tmp, _writable())
            fs.write('sub/a.txt', 'linha um\nlinha dois\n')
            self.assertTrue((Path(tmp) / 'sub/a.txt').is_file())
            self.assertEqual(fs.read('sub/a.txt')['content'], 'linha um\nlinha dois\n')
            res = fs.edit('sub/a.txt', 'linha dois', 'LINHA 2')
            self.assertIsNotNone(res['backup'])
            self.assertIn('LINHA 2', fs.read('sub/a.txt')['content'])
            self.assertEqual(fs.search('LINHA')['count'], 1)

    def test_write_requires_scope(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ScopeDenied):
                FsTools(tmp, AgentPolicy(READ_ONLY)).write('x.txt', 'y')

    def test_edit_ambiguous_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            fs = FsTools(tmp, _writable())
            fs.write('d.txt', 'xx')
            with self.assertRaises(PathEscape):
                fs.edit('d.txt', 'x', 'y')  # 2 ocorrências

    def test_traversal_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(PathEscape):
                FsTools(tmp, _writable()).read('../../etc/passwd')


class ExecToolsTests(unittest.TestCase):
    def test_safe_command_runs(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = ExecTools(tmp, _writable()).run('echo ola')
            self.assertEqual(out['returncode'], 0)
            self.assertIn('ola', out['stdout'])
            self.assertFalse(out['destructive'])

    def test_destructive_requires_confirmation(self):
        with tempfile.TemporaryDirectory() as tmp:
            denier = AgentPolicy({'exec'}, confirm=lambda a: False)
            with self.assertRaises(ConfirmationRequired):
                ExecTools(tmp, denier).run('rm -rf ./x')
            out = ExecTools(tmp, _writable()).run('rm -rf ./__nao_existe__')
            self.assertTrue(out['destructive'])

    def test_requires_exec_scope(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ScopeDenied):
                ExecTools(tmp, AgentPolicy(READ_ONLY)).run('echo hi')

    def test_timeout(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = ExecTools(tmp, _writable()).run('sleep 3', timeout=1)
            self.assertTrue(out['timed_out'])


class GitToolsTests(unittest.TestCase):
    def _repo(self, tmp):
        subprocess.run(['git', 'init', '-q', tmp], check=True)
        for k, v in (('user.email', 't@t'), ('user.name', 'T'), ('commit.gpgsign', 'false')):
            subprocess.run(['git', '-C', tmp, 'config', k, v], check=True)

    def test_force_rejected(self):
        with self.assertRaises(AgentError):
            _reject_force(['push', '--force', 'origin', 'main'])
        with self.assertRaises(AgentError):
            _reject_force(['push', 'origin', '+main'])

    def test_commit_and_push_to_local_remote(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as bare:
            self._repo(tmp)
            subprocess.run(['git', 'init', '-q', '--bare', bare], check=True)
            subprocess.run(['git', '-C', tmp, 'remote', 'add', 'origin', bare], check=True)
            (Path(tmp) / 'f.txt').write_text('hi')
            git = GitTools(tmp, _writable())
            git.add(['f.txt'])
            self.assertEqual(git.commit('primeiro')['returncode'], 0)
            self.assertEqual(git.push('origin', 'master' if (Path(tmp) / '.git/refs/heads/master').exists() else 'main')['returncode'], 0)

    def test_push_requires_scope(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._repo(tmp)
            with self.assertRaises(ScopeDenied):
                GitTools(tmp, AgentPolicy(READ_ONLY)).commit('x')


class RegistryTests(unittest.TestCase):
    def test_openai_tools_filtered_by_policy(self):
        with tempfile.TemporaryDirectory() as tmp:
            reg = register_builtin(Registry(AgentPolicy(READ_ONLY)), tmp)
            names = {t['function']['name'] for t in reg.openai_tools()}
            self.assertIn('fs_read', names)
            self.assertIn('git_status', names)
            self.assertNotIn('fs_write', names)
            self.assertNotIn('run_command', names)
            self.assertNotIn('git_push', names)

    def test_call_enforces_scope(self):
        with tempfile.TemporaryDirectory() as tmp:
            reg = register_builtin(Registry(AgentPolicy(READ_ONLY)), tmp)
            with self.assertRaises(ScopeDenied):
                reg.call('fs_write', {'path': 'x', 'content': 'y'})


class PluginTests(unittest.TestCase):
    def _make_plugin(self, root, scope='fs.read'):
        d = Path(root) / 'plugins' / 'demo'
        d.mkdir(parents=True)
        (d / 'handlers.py').write_text('def ola(**kw):\n    return {"msg": "oi do plugin"}\n')
        (d / 'plugin.json').write_text(json.dumps({
            'name': 'demo', 'version': '1.0.0', 'scopes': [scope],
            'tools': [{'name': 'demo_ola', 'description': 'oi', 'scope': scope,
                       'parameters': {'type': 'object', 'properties': {}, 'required': []},
                       'entry': 'handlers.py:ola'}],
        }))

    def test_manifest_rejects_undeclared_scope(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'plugin.json'
            p.write_text(json.dumps({'name': 'x', 'scopes': ['fs.read'],
                                     'tools': [{'name': 't', 'scope': 'exec', 'entry': 'h.py:f'}]}))
            with self.assertRaises(PluginError):
                load_manifest(p)

    def test_enable_loads_tool_disabled_does_not(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._make_plugin(tmp)
            mgr = PluginManager(tmp)
            self.assertFalse(mgr.list()[0]['enabled'])
            # desabilitado: não registra
            reg = Registry(AgentPolicy(READ_ONLY))
            self.assertEqual(mgr.load_into(reg), [])
            # habilitado: registra e roda
            mgr.enable('demo')
            reg2 = Registry(AgentPolicy(READ_ONLY))
            self.assertEqual(mgr.load_into(reg2), ['demo_ola'])
            self.assertEqual(reg2.call('demo_ola', {})['msg'], 'oi do plugin')
            mgr.disable('demo')
            self.assertEqual(mgr.load_into(Registry(AgentPolicy(READ_ONLY))), [])


class FakeClient:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def chat(self, scope, payload):
        self.calls.append(payload)
        return self.responses.pop(0)


def _tool_call(name, args):
    return {'choices': [{'message': {'content': None,
            'tool_calls': [{'id': 'c1', 'function': {'name': name, 'arguments': json.dumps(args)}}]}}]}


def _final(text):
    return {'choices': [{'message': {'content': text}}]}


class LoopTests(unittest.TestCase):
    def test_executes_tool_then_final(self):
        with tempfile.TemporaryDirectory() as tmp:
            reg = register_builtin(Registry(AgentPolicy(READ_ONLY)), tmp)
            client = FakeClient([_tool_call('fs_list', {'path': '.'}), _final('Listei tudo.')])
            events = []
            res = AgentLoop(reg, client=client).run('liste os arquivos', on_event=events.append)
            self.assertTrue(res['done'])
            self.assertEqual(res['answer'], 'Listei tudo.')
            self.assertEqual(res['iterations'], 2)
            self.assertTrue(any(e['type'] == 'tool' and e['ok'] for e in events))

    def test_blocked_scope_is_reported_not_crash(self):
        with tempfile.TemporaryDirectory() as tmp:
            reg = register_builtin(Registry(AgentPolicy(READ_ONLY)), tmp)  # fs.write NÃO liberado
            client = FakeClient([_tool_call('fs_write', {'path': 'x', 'content': 'y'}), _final('ok')])
            events = []
            res = AgentLoop(reg, client=client).run('escreva', on_event=events.append)
            self.assertTrue(res['done'])
            tool_events = [e for e in events if e['type'] == 'tool']
            self.assertTrue(tool_events and not tool_events[0]['ok'])

    def test_iteration_limit(self):
        with tempfile.TemporaryDirectory() as tmp:
            reg = register_builtin(Registry(AgentPolicy(READ_ONLY)), tmp)
            client = FakeClient([_tool_call('fs_list', {'path': '.'}) for _ in range(5)])
            res = AgentLoop(reg, client=client, max_iterations=3).run('loop', on_event=None)
            self.assertFalse(res['done'])
            self.assertEqual(res['iterations'], 3)


if __name__ == '__main__':
    unittest.main()
