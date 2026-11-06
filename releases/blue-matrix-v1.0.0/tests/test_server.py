"""Isolated smoke test using a local mock provider; no real tokens spent."""
import importlib.util
import json
import os
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import unittest


class MockProvider(BaseHTTPRequestHandler):
    def do_POST(self):
        n = int(self.headers.get('Content-Length', 0))
        req = json.loads(self.rfile.read(n))
        reply = 'Teste: ' + req['messages'][-1]['content']
        data = json.dumps({'choices': [{'message': {'content': reply}}]}).encode()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):
        pass


class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock = ThreadingHTTPServer(('127.0.0.1', 0), MockProvider)
        cls.mock_thread = Thread(target=cls.mock.serve_forever, daemon=True)
        cls.mock_thread.start()
        os.environ['SAGAZ_ADMIN_PASSWORD'] = 'password_used_only_in_test'
        os.environ['SAGAZ_SESSION_SECRET'] = 's' * 48
        os.environ['SAGAZ_API_KEY'] = 'test-key-never-send-to-client'
        os.environ['SAGAZ_UPSTREAM_URL'] = f'http://127.0.0.1:{cls.mock.server_port}/v1/chat/completions'
        path = Path(__file__).resolve().parents[1] / 'server' / 'sagaz_server.py'
        spec = importlib.util.spec_from_file_location('sagaz_runtime_test', path)
        cls.mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.mod)
        cls.srv = ThreadingHTTPServer(('127.0.0.1', 0), cls.mod.App)
        cls.thread = Thread(target=cls.srv.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f'http://127.0.0.1:{cls.srv.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()
        cls.mock.shutdown()

    def request(self, path, body=None, cookie=None, headers=None):
        h = headers or {}
        if body is not None:
            h.update({'Content-Type': 'application/json', 'X-SagaZ-Request': '1'})
        if cookie:
            h['Cookie'] = cookie
        req = Request(self.url + path, data=json.dumps(body).encode() if body is not None else None, headers=h)
        try:
            with urlopen(req, timeout=3) as r:
                return r.status, dict(r.headers), r.read()
        except HTTPError as e:
            return e.code, dict(e.headers), e.read()

    def test_static_public_but_not_internal_files(self):
        status, headers, body = self.request('/')
        self.assertEqual(status, 200)
        self.assertIn(b'HooLeeSh33t', body)
        self.assertIn(b'app.js', body)
        self.assertEqual(self.request('/creator')[0], 200)
        self.assertEqual(self.request('/apps/hooleesh33t-matrix-v1/styles.css')[0], 200)
        self.assertEqual(self.request('/apps/dsant-creator-v1/app.js')[0], 200)
        self.assertNotIn(b'test-key-never-send-to-client', body)
        self.assertEqual(self.request('/server/sagaz_server.py')[0], 404)
        self.assertEqual(self.request('/docs/SEGURANCA.md')[0], 404)

    def test_auth_and_mock_chat(self):
        status, _, body = self.request('/api/v1/status')
        self.assertEqual(status, 200)
        self.assertFalse(json.loads(body)['chat'])
        self.assertEqual(self.request('/api/v1/chat', {'message': 'Teste'})[0], 401)
        self.assertEqual(self.request('/api/v1/login', {'password': 'wrong'})[0], 401)
        status, h, _ = self.request('/api/v1/login', {'password': 'password_used_only_in_test'})
        self.assertEqual(status, 200)
        cookie = h['Set-Cookie'].split(';')[0]
        status, _, body = self.request('/api/v1/status', cookie=cookie)
        self.assertTrue(json.loads(body)['chat'])
        status, _, body = self.request('/api/v1/chat', {'message': 'funciona'}, cookie=cookie)
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)['reply'], 'Teste: funciona')
        self.assertEqual(self.request('/api/v1/chat/reset', {}, cookie=cookie)[0], 200)

    def test_csrf_header_required(self):
        status, _, _ = self.request('/api/v1/login', {'password': 'password_used_only_in_test'}, headers={'Origin': 'https://evil.invalid'})
        self.assertEqual(status, 403)
        req = Request(self.url + '/api/v1/login', data=b'{}', headers={'Content-Type': 'application/json'})
        with self.assertRaises(HTTPError) as err:
            urlopen(req, timeout=3)
        self.assertEqual(err.exception.code, 403)

if __name__ == '__main__':
    unittest.main()
