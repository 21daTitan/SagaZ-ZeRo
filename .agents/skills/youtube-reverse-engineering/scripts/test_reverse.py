import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec=importlib.util.spec_from_file_location('reverse',Path(__file__).with_name('reverse.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class ReverseTests(unittest.TestCase):
    def test_intake_local_vtt_and_draft(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);vtt=p/'captions.vtt';vtt.write_text('WEBVTT\n\n00:00.000 --> 00:02.000\nUm painel apagou.\n\n00:02.000 --> 00:05.000\nAntes de trocar, peça avaliação.\n')
            meta=p/'meta.json';meta.write_text(json.dumps({'title':'Teste autoral','duration':5}))
            result=m.acquire('https://youtu.be/abcdefghijk',p/'out',vtt,meta)
            self.assertEqual(result['segments'],2)
            d=json.loads((p/'out/dossier.json').read_text())
            self.assertIsNone(m.validate(d)['editorial_average'])
            self.assertFalse(d['evidence']['visual'])
            with self.assertRaises(FileExistsError):m.acquire('https://youtu.be/abcdefghijk',p/'out',vtt,meta)

    def test_json3_and_invalid_segments(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'caption.json3';p.write_text(json.dumps({'events':[{'tStartMs':1000,'dDurationMs':2000,'segs':[{'utf8':'Olá '},{'utf8':'mundo'}]}]}))
            self.assertEqual(m.parse_transcript(p),[{'start':1,'end':3,'text':'Olá mundo'}])
            p.write_text('[{"start":3,"end":2,"text":"erro"}]')
            with self.assertRaises(ValueError):m.parse_transcript(p)

    def test_local_evidence_without_url(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);vtt=p/'own.vtt';vtt.write_text('00:00.000 --> 00:02.000\nLegenda autoral.\n')
            m.acquire(None,p/'out',transcript=vtt)
            data=json.loads((p/'out/dossier.json').read_text())
            self.assertIsNone(data['source']['url'])
            self.assertTrue(m.validate(data)['valid'])

    def test_url_boundary(self):
        self.assertEqual(m.canonical('https://youtube.com/shorts/abcdefghijk'),'https://www.youtube.com/watch?v=abcdefghijk')
        for url in ['https://youtube.com.evil/watch?v=abcdefghijk','http://youtu.be/abcdefghijk','https://youtube.com/playlist?list=abcdefghijk']:
            with self.assertRaises(ValueError):m.canonical(url)

    def test_unseen_cuts_and_reviewed_gate(self):
        d=json.loads((m.ROOT/'references/dossier-template.json').read_text());d['source']['url']='https://youtu.be/abcdefghijk';d['source']['duration_seconds']=10
        d['beats']=[dict(start=0,end=10,function='gancho',evidence='legenda 0–10 s',cuts_per_second=2)]
        with self.assertRaises(ValueError):m.validate(d)
        d['beats'][0]['cuts_per_second']=None;d['status']='reviewed'
        with self.assertRaises(ValueError):m.validate(d)
        d.update(status='draft');d['scorecard']['hook']={'score':8,'reason':'promessa identificada; hipótese editorial'}
        self.assertEqual(m.validate(d)['editorial_average'],8)
        d['scorecard']['hook']['score']=float('nan')
        with self.assertRaises(ValueError):m.validate(d)

if __name__=='__main__':unittest.main()
