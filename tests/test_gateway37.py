"""Offline regression tests for v3.7 gateway, policy, cost and integrity."""
import http.client
import json
import os
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch

from sagaz.app import Server
from sagaz.gateway.audit import AuditLedger, redact
from sagaz.gateway.capabilities import Capability, CapabilityCache
from sagaz.gateway.cost import CostMeter
from sagaz.gateway.policy import RateLimiter, PUBLIC, LOCAL_UI, TOKEN_API, authenticate
from sagaz.gateway.skills import select_skill
from sagaz.gateway.mcp import dispatch


class GatewayModulesTests(unittest.TestCase):
    def test_ttl_cache_refresh_and_connector_isolation(self):
        clock = [10]
        cache = CapabilityCache(clock=lambda: clock[0])
        calls = []
        def load(connector):
            calls.append(connector)
            return Capability(connector, 'model')
        self.assertEqual(cache.get_or_load('A', 'model', lambda: load('A')).connector, 'A')
        cache.get_or_load('A', 'model', lambda: load('A'))
        cache.get_or_load('B', 'model', lambda: load('B'))
        self.assertEqual(calls, ['A', 'B'])
        clock[0] = 71
        cache.get_or_load('A', 'model', lambda: load('A'))
        self.assertEqual(calls, ['A', 'B', 'A'])

    def test_connector_scopes_cannot_be_spoofed(self):
        self.assertEqual(authenticate(None, 'private-session', None, None), PUBLIC)
        self.assertEqual(authenticate('private-session', 'private-session', None, None), LOCAL_UI)
        self.assertEqual(authenticate(None, 'private-session', 'opaque-1234', 'opaque-1234'), TOKEN_API)
        self.assertNotIn('shell', LOCAL_UI.tools)
        self.assertFalse(TOKEN_API.shell)

    def test_rate_limit_is_per_connector(self):
        now = [1.0]
        limiter = RateLimiter({'local-ui': (2, 5), 'token-api': (1, 5)}, lambda: now[0])
        self.assertTrue(limiter.allow('local-ui'))
        self.assertTrue(limiter.allow('local-ui'))
        self.assertFalse(limiter.allow('local-ui'))
        self.assertTrue(limiter.allow('token-api'))
        self.assertFalse(limiter.allow('token-api'))
        now[0] = 7.0
        self.assertTrue(limiter.allow('local-ui'))
        self.assertTrue(limiter.allow('token-api'))

    def test_skill_routes_one_only(self):
        self.assertEqual(select_skill('Preciso de copy e CTA para uma oferta').name, 'merovingian')
        self.assertEqual(select_skill('Engenharia reversa de video YouTube').name, 'rataria')
        self.assertIsNone(select_skill('Reunião para discutir o tempo').name)

    def test_audit_chain_tamper_checkpoint_and_redact(self):
        with tempfile.TemporaryDirectory() as root:
            file = Path(root) / 'audit.jsonl'
            ledger = AuditLedger(file, key='signed-checkpoint-secret')
            ledger.append('request', {'authorization': 'Bearer raw-sensitive-abcdefghi',
                                      'url': 'https://demo.invalid/endpoint?api_key=sensitive&safe=ok'})
            ledger.append('completion', {'connector': 'token-api'})
            data = file.read_text(encoding='utf-8')
            self.assertNotIn('raw-sensitive', data)
            self.assertNotIn('sensitive&', data)
            self.assertIn('[REDACTED]', data)
            self.assertEqual(ledger.verify()['records'], 2)
            checkpoint = ledger.checkpoint()
            self.assertTrue(ledger.verify_checkpoint(checkpoint))
            modified = data.replace('token-api', 'external', 1)
            file.write_text(modified, encoding='utf-8')
            self.assertFalse(ledger.verify()['valid'])
            self.assertFalse(ledger.verify_checkpoint(checkpoint))
            with self.assertRaises(ValueError):
                ledger.append('request', {})

    def test_cost_usage_only_measured_when_provider_supplies_usage(self):
        with tempfile.TemporaryDirectory() as root:
            meter = CostMeter(Path(root) / 'usage.jsonl')
            item = meter.record('token-api', 'm1', {'prompt_tokens': 1500, 'completion_tokens': 100}, '1.00', '2.00')
            self.assertEqual(item['usd'], '0.0017')
            meter.record('local-ui', 'm2', {'prompt_tokens': 1, 'completion_tokens': 2})
            report = meter.report()
            self.assertEqual(report['count'], 2)
            self.assertEqual(report['unpriced_requests'], 1)
            self.assertIsNone(report['at_or_above_80_pct'])
            with self.assertRaises(ValueError):
                meter.record('a', 'm', {'prompt_tokens': -1, 'completion_tokens': 2})

    def test_mcp_tools_resources_prompts(self):
        for method, key in [('initialize', 'serverInfo'), ('tools/list', 'tools'),
                            ('resources/list', 'resources'), ('prompts/list', 'prompts')]:
            result = dispatch({'jsonrpc': '2.0', 'id': 1, 'method': method}, TOKEN_API)
            self.assertIn(key, result['result'])
        result = dispatch({'jsonrpc': '2.0', 'id': 2, 'method': 'resources/read',
                           'params': {'uri': 'sagaz://provenance'}}, TOKEN_API)
        self.assertIn('Mörlsara', result['result']['contents'][0]['text'])
        denied = dispatch({'jsonrpc': '2.0', 'id': 3, 'method': 'tools/call',
                           'params': {'name': 'fs_write'}}, TOKEN_API)
        self.assertEqual(denied['error']['code'], -32003)
        allowed = dispatch({'jsonrpc': '2.0', 'id': 4, 'method': 'tools/call',
                            'params': {'name': 'sagaz_status'}}, TOKEN_API)
        self.assertIn('Morlsara Code Nexus', allowed['result']['content'][0]['text'])


class GatewayHttpTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.server = Server(('127.0.0.1', 0), Path(self.tmp.name) / 'tasks')
        self.worker = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.worker.start()
        self.cookie = ''

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.worker.join(timeout=3)
        self.tmp.cleanup()

    def call(self, verb, route, data=None, headers=None):
        connection = http.client.HTTPConnection('127.0.0.1', self.server.server_port, timeout=10)
        headers = dict(headers or {})
        headers['Host'] = f'127.0.0.1:{self.server.server_port}'
        if isinstance(data, dict):
            data = json.dumps(data)
            headers['Content-Type'] = 'application/json'
        connection.request(verb, route, body=data, headers=headers)
        response = connection.getresponse()
        body = response.read()
        status = response.status
        output_headers = dict(response.getheaders())
        connection.close()
        try:
            body = json.loads(body)
        except (ValueError, UnicodeDecodeError):
            pass
        return status, output_headers, body

    def login(self):
        status, header, _ = self.call('GET', '/')
        self.assertEqual(status, 200)
        self.cookie = header['Set-Cookie'].split(';')[0]

    def test_private_data_requires_cookie(self):
        status, _, _ = self.call('GET', '/api/projects')
        self.assertEqual(status, 403)
        status, _, _ = self.call('GET', '/gateway/cost')
        self.assertEqual(status, 403)
        self.login()
        status, _, data = self.call('GET', '/api/projects', headers={'Cookie': self.cookie})
        self.assertEqual(status, 200)
        self.assertEqual(data, [])

    def test_authenticated_mcp_and_skills(self):
        self.login()
        headers = {'Cookie': self.cookie}
        status, _, data = self.call('POST', '/mcp', {'jsonrpc': '2.0', 'id': 1, 'method': 'tools/list'}, headers)
        self.assertEqual(status, 200)
        self.assertTrue(any(item['name'] == 'sagaz_status' for item in data['result']['tools']))
        status, _, data = self.call('POST', '/gateway/skills/select', {'text': 'copy de oferta e CTA'}, headers)
        self.assertEqual(status, 200)
        self.assertEqual(data['skill'], 'merovingian')
        status, _, data = self.call('GET', '/gateway/audit/verify', headers=headers)
        self.assertTrue(data['valid'])
        self.assertEqual(data['records'], 2)

    def test_token_does_not_grant_browser_task_or_shell(self):
        with patch.dict(os.environ, {'SAGAZ_API_TOKEN': 'opaque-token-for-test'}):
            headers = {'Authorization': 'Bearer opaque-token-for-test', 'X-Connector': 'claude_code'}
            status, _, _ = self.call('POST', '/api/chat', {'brief': 'Teste'}, headers)
            self.assertEqual(status, 402)
            status, _, data = self.call('POST', '/mcp', {'jsonrpc': '2.0', 'id': 1,
                            'method': 'tools/call', 'params': {'name': 'shell'}}, headers)
            self.assertEqual(status, 200)
            self.assertEqual(data['error']['code'], -32003)

    def test_chat_requires_configured_provider(self):
        self.login()
        with patch.dict(os.environ, {'DSANT_BASE_URL': '', 'DSANT_MODEL': ''}):
            status, _, data = self.call('POST', '/v1/chat/completions',
                                       {'messages': [{'role': 'user', 'content': 'test'}]},
                                       {'Cookie': self.cookie})
        self.assertEqual(status, 503)
        self.assertIn('DSANT_BASE_URL', data['error'])

    def test_simulated_provider_cost_and_budget(self):
        self.login()
        import sagaz.gateway.service as service
        with patch.dict(os.environ, {'DSANT_BASE_URL': 'http://127.0.0.1:11434/v1', 'DSANT_MODEL': 'local-model',
                                     'SAGAZ_INPUT_USD_PER_M': '1', 'SAGAZ_OUTPUT_USD_PER_M': '2',
                                     'SAGAZ_BUDGET_USD': '0.01'}):
            payload = {'messages': [{'role': 'user', 'content': 'test'}], 'model': 'local-model'}
            mock_response = {'object': 'chat.completion', 'choices': [{'message': {'role': 'assistant', 'content': 'ok'}}],
                             'usage': {'prompt_tokens': 1000, 'completion_tokens': 500}}
            with patch.object(service, 'complete', return_value=mock_response) as remote:
                status, _, _ = self.call('POST', '/v1/chat/completions', payload, {'Cookie': self.cookie})
                self.assertEqual(status, 200)
                remote.assert_called_once()
            status, _, report = self.call('GET', '/gateway/cost', headers={'Cookie': self.cookie})
            self.assertEqual(status, 200)
            self.assertEqual(report['total_known_usd'], '0.002')
            self.assertEqual(report['count'], 1)


if __name__ == '__main__':
    unittest.main()
