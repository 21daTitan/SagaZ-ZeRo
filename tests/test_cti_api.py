import http.client
import json
import threading
import unittest
from pathlib import Path
import tempfile

from sagaz.app import Server
from sagaz.gateway.mcp import dispatch
from sagaz.gateway.policy import LOCAL_UI, PUBLIC, TOKEN_API


class CTIAPITests(unittest.TestCase):
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

    def call(self, route, headers=None):
        connection = http.client.HTTPConnection('127.0.0.1', self.server.server_port, timeout=5)
        request_headers = {'Host': f'127.0.0.1:{self.server.server_port}'}
        request_headers.update(headers or {})
        connection.request('GET', route, headers=request_headers)
        response = connection.getresponse()
        status, headers, body = response.status, dict(response.getheaders()), response.read()
        connection.close()
        try:
            body = json.loads(body)
        except (ValueError, UnicodeDecodeError):
            body = body.decode('utf-8')
        return status, headers, body

    def call_mcp_summary(self):
        connection = http.client.HTTPConnection('127.0.0.1', self.server.server_port, timeout=5)
        payload = {'jsonrpc': '2.0', 'id': 8, 'method': 'tools/call',
                   'params': {'name': 'sagaz_cti_summary'}}
        headers = {'Host': f'127.0.0.1:{self.server.server_port}',
                   'Origin': f'http://127.0.0.1:{self.server.server_port}',
                   'Cookie': self.cookie, 'Content-Type': 'application/json'}
        connection.request('POST', '/mcp', body=json.dumps(payload), headers=headers)
        response = connection.getresponse()
        status, body = response.status, json.loads(response.read())
        connection.close()
        return status, body

    def login(self):
        status, headers, _ = self.call('/')
        self.assertEqual(status, 200)
        self.cookie = headers.get('Set-Cookie', '').split(';')[0]

    def test_api_requires_session_and_records_audit(self):
        self.assertEqual(self.call('/api/cti/summary')[0], 403)
        self.login()
        status, _, data = self.call('/api/cti/summary', {'Cookie': self.cookie})
        self.assertEqual(status, 200)
        self.assertEqual(data['count'], 10)
        self.assertEqual(data['status_counts'], {'unverified': 10})
        status, mcp = self.call_mcp_summary()
        self.assertEqual(status, 200)
        self.assertIn('unverified', mcp['result']['content'][0]['text'])
        audit = self.server.gateway.audit.verify()
        self.assertEqual(audit['records'], 3)

    def test_api_search_parameters_and_limit(self):
        self.login()
        headers = {'Cookie': self.cookie}
        status, _, data = self.call('/api/cti/search?q=Emotet&limit=1', headers)
        self.assertEqual(status, 200)
        self.assertEqual(data['results'][0]['title'], 'Emotet')
        for route in ('/api/cti/search', '/api/cti/search?q=',
                      '/api/cti/search?q=Emotet&q=FIN7',
                      '/api/cti/search?q=Emotet&limit=51',
                      '/api/cti/search?q=Emotet&other=x',
                      '/api/cti/summary?unexpected=1'):
            with self.subTest(route=route):
                self.assertEqual(self.call(route, headers)[0], 400)

    def test_mcp_catalog_tools_are_scoped_validated_and_audited(self):
        payload = {'jsonrpc': '2.0', 'id': 1, 'method': 'tools/call',
                   'params': {'name': 'sagaz_cti_search', 'arguments': {'q': 'G0046'}}}
        denied = dispatch(payload, PUBLIC)
        self.assertEqual(denied['error']['code'], -32003)
        allowed = dispatch(payload, TOKEN_API)
        self.assertIn('ALFA-CTI-0014', allowed['result']['content'][0]['text'])
        invalid = dispatch({**payload, 'params': {'name': 'sagaz_cti_search',
                          'arguments': {'q': 'FIN7', 'shell': 'no'}}}, LOCAL_UI)
        self.assertEqual(invalid['error']['code'], -32602)
        summary_result = dispatch({'jsonrpc': '2.0', 'id': 2, 'method': 'tools/call',
                                   'params': {'name': 'sagaz_cti_summary'}}, TOKEN_API)
        self.assertIn('unverified', summary_result['result']['content'][0]['text'])


if __name__ == '__main__':
    unittest.main()