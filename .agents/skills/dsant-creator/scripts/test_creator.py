import argparse
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec=importlib.util.spec_from_file_location('creator', Path(__file__).with_name('creator.py'))
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)

class CreatorTests(unittest.TestCase):
    def args(self,out,**kw):
        data=dict(out=str(out),brief='Copy para reparo de painel RR',niche='automotive',method='automotive-pov',route='remotion',task=None,state_dir=None)
        data.update(kw);return argparse.Namespace(**data)

    def test_url_canonical_and_reject(self):
        self.assertEqual(c.canonical('https://youtu.be/1vDxSy3xov4?si=abc')[1],'https://www.youtube.com/watch?v=1vDxSy3xov4')
        for url in ['http://youtube.com/watch?v=1vDxSy3xov4','https://youtube.com.evil/watch?v=1vDxSy3xov4','https://localhost/a','https://youtube.com/watch?v=abc','https://user:secret@youtube.com/watch?v=1vDxSy3xov4','https://youtube.com/playlist?list=abc']:
            with self.assertRaises(ValueError):c.canonical(url)

    def test_prepare_isolation_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'campaign';c.prepare(self.args(p))
            self.assertTrue(c.validate(p)['valid'])
            self.assertTrue(all(x['scope']=='generic' for x in c.read(p/'campaign.json')['sources']))
            with self.assertRaises(FileExistsError):c.prepare(self.args(p))
            h=Path(td)/'hot';c.prepare(self.args(h,niche='hot'))
            self.assertTrue(any(x['scope']=='hot' for x in c.read(h/'campaign.json')['sources']))

    def test_tamper_detected(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'campaign';c.prepare(self.args(p))
            path=p/'history.jsonl';path.write_text(path.read_text().replace('prepared','tampered'))
            with self.assertRaises(ValueError):c.validate(p)
            with self.assertRaises(ValueError):c.append_event(p,'test','note')

    def test_registry_and_routing(self):
        self.assertGreaterEqual(len(c.registry()['entries']),20)
        self.assertEqual(c.choose_task('Crie vídeo MP4'), 'video')
        self.assertEqual(c.choose_task('estratégia de CTA'), 'strategy')
        self.assertEqual(c.choose_task('analise esse vídeo https://youtu.be/1vDxSy3xov4'), 'reference')

    def test_run_config_and_transport(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'campaign';c.prepare(self.args(p))
            with patch.dict(os.environ,{},clear=True):
                with self.assertRaises(ValueError):c.run(p)
            with patch.dict(os.environ,dict(DSANT_BASE_URL='http://example.com/v1',DSANT_MODEL='test',DSANT_API_KEY='test'),clear=True):
                with self.assertRaises(ValueError):c.run(p)
            class Response:
                def __enter__(self):return self
                def __exit__(self,*a):pass
                def read(self,n):return json.dumps({'choices':[{'message':{'content':'Texto de teste'}}]}).encode()
            with patch.dict(os.environ,dict(DSANT_BASE_URL='http://localhost:11434/v1',DSANT_MODEL='test'),clear=True),patch.object(c,'urlopen',return_value=Response()) as mock:
                result=c.run(p)
                self.assertEqual(Path(result['output']).read_text(),'Texto de teste')
                payload=json.loads(mock.call_args.args[0].data)
                self.assertEqual(payload['model'],'test')
            self.assertEqual(c.read(p/'campaign.json')['status'],'prepared')
            self.assertTrue(c.validate(p)['valid'])

if __name__=='__main__':unittest.main()
