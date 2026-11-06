import importlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class ProvenanceTests(unittest.TestCase):
    def test_attribution_immutable_marker(self):
        a = importlib.import_module('sagaz.attribution')
        self.assertEqual(a.ORIGIN_MARK, 'Morlsara Code Nexus')
        self.assertEqual(a.UPSTREAM_AUTHOR, 'Mörlsara')
        self.assertEqual(a.UPSTREAM_GROUP, 'Code Nexus')
        self.assertIn('DarkyHArry/cassandra-agent', a.UPSTREAM_REPO)
        self.assertEqual(a.FORK_VERSION, (ROOT/'VERSION').read_text().strip())
        self.assertEqual(a.FORK_ORGANIZATION, 'Systemia Solutions')
        self.assertEqual(a.PERSONA_LAYER, 'HooLeeSheet')
        self.assertTrue(a.verify())
        self.assertIn('Morlsara Code Nexus',a.machine_tag())
        self.assertIn('Code Nexus',a.attribution_trailer())

    def test_provenance_in_files(self):
        for filename in ('README.md', 'NOTICE.md', 'FORK.md'):
            text = (ROOT/filename).read_text(encoding='utf-8')
            self.assertIn('Mörlsara', text, filename)
            self.assertIn('Code Nexus', text, filename)
            self.assertIn('DarkyHArry/cassandra-agent', text, filename)

if __name__=='__main__': unittest.main()
