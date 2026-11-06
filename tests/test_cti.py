"""CTI integration regression checks using only local standard library."""
import json
from pathlib import Path
import tempfile
import unittest
from sagaz.cti import records, search, summary

class CTIIntegrationTests(unittest.TestCase):
    def test_dataset_count_and_ids(self):
        data = records()
        self.assertEqual(len(data), 10)
        self.assertEqual(len({row['knowledge_id'] for row in data}), 10)
        self.assertEqual(summary()['verified'], 0)
    def test_search_case_and_accents(self):
        result = search('emotet')
        self.assertEqual(result['count'], 1)
        self.assertEqual(result['entries'][0]['knowledge_id'], 'ALFA-CTI-0013')
    def test_search_input_restrictions(self):
        for query in ('', 'x'*121):
            with self.assertRaises(ValueError): search(query)
        for limit in (0, 21, True, '2'):
            with self.assertRaises(ValueError): search('conti', limit)
    def test_external_verified_is_demoted(self):
        row = records()[0]
        with tempfile.TemporaryDirectory() as directory:
            row['evidence_status'] = 'verified'
            path = Path(directory) / 'fake.json'
            path.write_text(json.dumps([row]))
            self.assertEqual(records(path)[0]['evidence_status'], 'unverified')
    def test_duplicate_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'dups.json'
            path.write_text(json.dumps([records()[0],records()[0]]))
            with self.assertRaises(ValueError): records(path)
if __name__ == '__main__': unittest.main()
