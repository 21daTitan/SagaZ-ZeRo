import http.client
import json
from pathlib import Path
import tempfile
import threading
import unittest
from sagaz.app import Server

ROOT = Path(__file__).resolve().parents[1]

class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.server=Server(('127.0.0.1',0),Path(self.temp.name))
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)
        self.temp.cleanup()

    def get(self,path):
        conn=http.client.HTTPConnection('127.0.0.1',self.server.server_port,timeout=5)
        conn.request('GET',path,headers={'Host':f'127.0.0.1:{self.server.server_port}'})
        resp=conn.getresponse();body=resp.read();code=resp.status;conn.close()
        return code,json.loads(body)

    def test_health_and_credits(self):
        code,data=self.get('/healthz')
        self.assertEqual(code,200)
        self.assertEqual(data['version'],'3.7.0-zeRo')
        code,data=self.get('/api/attribution')
        self.assertEqual(code,200)
        self.assertEqual(data['inspiration']['author'],'Mörlsara')
        self.assertEqual(data['persona'],'HooLeeSheet')

    def test_gateway_connectors_metadata_only(self):
        code,data=self.get('/gateway/connectors')
        self.assertEqual(code,200)
        self.assertFalse(data['shell_enabled'])
        self.assertTrue(any(x['name']=='local' for x in data['entries']))
        self.assertFalse(any('key' in x for x in data['entries']))

    def test_mobile_branding(self):
        html=(ROOT/'sagaz/index.html').read_text()
        self.assertIn('HooLeeSheet',html)
        self.assertIn('Systemia Solutions',html)
        self.assertIn('viewport',html)
        self.assertIn('id="rain"',html)

if __name__=='__main__': unittest.main()
