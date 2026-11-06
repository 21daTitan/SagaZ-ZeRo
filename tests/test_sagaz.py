import http.client
import importlib.util
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch

R=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('sagaz_test_app',R/'sagaz/app.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)

class SagaZTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.server=m.Server(('127.0.0.1',0),Path(self.temp.name))
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
        self.host=f'127.0.0.1:{self.server.server_port}';self.cookie=''
    def tearDown(self):
        self.server.shutdown();self.server.server_close();self.thread.join();self.temp.cleanup()
    def request(self,method,path,body=None,headers=None):
        conn=http.client.HTTPConnection('127.0.0.1',self.server.server_port,timeout=5)
        conn.request(method,path,body=body,headers=headers or {});r=conn.getresponse();content=r.read();h=dict(r.getheaders());status=r.status;conn.close();return status,h,content
    def login(self):
        status,h,b=self.request('GET','/');self.assertEqual(status,200)
        self.assertIn(b'SAGAZ',b);self.cookie=h['Set-Cookie'].split(';')[0]
    def test_local_chat_exports_real_context_without_model(self):
        self.login()
        headers={'Cookie':self.cookie,'Content-Type':'application/json','Origin':'http://'+self.host}
        with patch.object(m.CORE,'run') as remote:
            status,h,b=self.request('POST','/api/chat',json.dumps({'brief':'Campanha RR sobre painel apagado','niche':'automotive'}),headers)
            self.assertEqual(status,200);remote.assert_not_called()
        d=json.loads(b);self.assertEqual(d['mode'],'local_preparation')
        status,h,b=self.request('GET','/api/context/'+d['id'],headers={'Cookie':self.cookie});self.assertEqual(status,200);self.assertIn('Campanha RR',b.decode())
        status,h,b=self.request('GET','/api/projects',headers={'Cookie':self.cookie});self.assertEqual(len(json.loads(b)),1)
    def test_csrf_host_and_invalid_scope(self):
        body=json.dumps({'brief':'Teste'})
        status,_,_=self.request('POST','/api/chat',body,{'Content-Type':'application/json'});self.assertEqual(status,403)
        self.login()
        headers={'Cookie':self.cookie,'Content-Type':'application/json','Origin':'https://example.invalid'}
        status,_,_=self.request('POST','/api/chat',body,headers);self.assertEqual(status,403)
        status,_,_=self.request('GET','/api/status',headers={'Host':'evil.invalid'});self.assertEqual(status,421)
        headers['Origin']='http://'+self.host
        status,_,_=self.request('POST','/api/chat',json.dumps({'brief':'x','niche':'invalid'}),headers);self.assertEqual(status,400)
    def test_private_configuration_and_path_boundaries(self):
        with patch.dict(m.os.environ,{'DSANT_API_KEY':'secret-test-value','DSANT_BASE_URL':'https://example.invalid/v1','DSANT_MODEL':'test'}):
            status,_,body=self.request('GET','/api/status');self.assertEqual(status,200);self.assertNotIn(b'secret-test-value',body)
        self.login()
        status,_,_=self.request('GET','/api/context/../../etc/passwd',headers={'Cookie':self.cookie});self.assertEqual(status,400)
    def test_youtube_routing_is_not_claimed_complete(self):
        d=m.prepare_task('Estude https://youtu.be/abcdefghijk',state_root=Path(self.temp.name))
        self.assertEqual(d['procedure'],'youtube-reverse-engineering');self.assertEqual(d['status'],'prepared')

    def test_resume_preserves_versions_and_isolates_niches(self):
        state=Path(self.temp.name)
        first=m.prepare_task('Primeiro objetivo da campanha RR',niche='automotive',state_root=state)
        original=(state/first['id']/'conversation.json').read_bytes()
        second=m.prepare_task('Agora ajuste o gancho',niche='automotive',state_root=state,parent_id=first['id'])
        self.assertNotEqual(first['id'],second['id'])
        self.assertEqual((state/first['id']/'conversation.json').read_bytes(),original)
        self.assertIn('Primeiro objetivo', (state/second['id']/'context.md').read_text())
        self.login()
        status,_,body=self.request('GET','/api/conversation/'+second['id'],headers={'Cookie':self.cookie})
        self.assertEqual(status,200);self.assertEqual(len(json.loads(body)['messages']),4)
        for parent in ('../outside','0'*32):
            with self.assertRaises(ValueError):m.prepare_task('Teste',state_root=state,parent_id=parent)
        with self.assertRaises(ValueError):m.prepare_task('Outro nicho',niche='hot',state_root=state,parent_id=first['id'])

    def test_static_catalog_and_connection_never_expose_credentials(self):
        for path,kind in [('/assets/app.css','text/css'),('/assets/app.js','text/javascript')]:
            status,headers,body=self.request('GET',path)
            self.assertEqual(status,200);self.assertIn(kind,headers['Content-Type'])
            self.assertIn("script-src 'self';",headers['Content-Security-Policy'])
        status,_,body=self.request('GET','/api/skills');self.assertEqual(status,200)
        data=json.loads(body);self.assertEqual(data['count'],7)
        self.assertTrue(all(len(item['description'])>20 for item in data['entries']))
        with patch.dict(m.os.environ,{'DSANT_API_KEY':'secret-test-value','DSANT_BASE_URL':'https://example.invalid/v1','DSANT_MODEL':'my-model'}):
            self.login()
            status,_,body=self.request('GET','/api/connection',headers={'Cookie':self.cookie})
            self.assertEqual(status,200);self.assertNotIn(b'secret-test-value',body)
            self.assertEqual(json.loads(body)['model'],'my-model')

s2=importlib.util.spec_from_file_location('reverse_tests',R/'.agents/skills/youtube-reverse-engineering/scripts/test_reverse.py');rt=importlib.util.module_from_spec(s2);s2.loader.exec_module(rt)
ReverseTests=rt.ReverseTests
if __name__=='__main__':unittest.main()
