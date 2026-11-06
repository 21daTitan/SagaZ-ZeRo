import importlib.util
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('learning',ROOT/'.agents/skills/dsant-creator/scripts/creator.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)

class PlaylistLearningTests(unittest.TestCase):
    def test_manifest_keeps_evidence_and_resolves_notes(self):
        folder=ROOT/'knowledge/playlists/PLBPobzL8BYoHZPSfnfrPR02eE5Xb4JeLi'
        manifest=json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
        self.assertEqual(sum(e['state']=='sampled' for e in manifest['entries']),15)
        self.assertEqual(sum(e['state']=='unavailable' for e in manifest['entries']),1)
        for e in manifest['entries']:
            if e.get('study'):self.assertTrue((folder/e['study']).is_file())

    def test_generic_retrieval_is_attributed_and_scoped(self):
        notes=m.select_studies('copy CTA RR painel','automotive')
        self.assertEqual(len(notes),3)
        self.assertTrue(all(e['scope']=='generic' and e['evidence']=='sampled' and e['full_study_pending'] for e in notes))
        self.assertTrue(any(e['id']=='TydXOf_o46Q' for e in notes))

    def test_hot_retrieval_keeps_explicit_scope(self):
        notes=m.select_studies('copy criativo hot','hot')
        self.assertTrue(any(e['scope']=='hot' for e in notes))
        self.assertTrue(all('Fonte:' in e['text'] for e in notes))

if __name__=='__main__':unittest.main()
