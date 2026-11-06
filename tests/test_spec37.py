"""Non-destructive upgrade, reverse-compat and static PIX invariants."""
from pathlib import Path
import json
import tempfile
import unittest
import zipfile
from sagaz.pix import static_brcode, crc16
from sagaz.rename import transform
from sagaz.compat.upstream import compare_directories
from sagaz.compat.report import markdown
from tools.safe_merge import stage


class Spec37Tests(unittest.TestCase):
    def test_pix_emv_crc_and_no_fake_default(self):
        with self.assertRaises(ValueError):
            static_brcode(key='')
        code=static_brcode(key='test-key-user-supplied',name='D SANT',city='RIO DE JANEIRO')
        self.assertIn('br.gov.bcb.pix',code)
        self.assertTrue(code.endswith('6304'+crc16(code[:-4])))
        self.assertIn('5906D SANT', code)

    def test_protected_attribution_not_renamed(self):
        original='Evil Cassandra\n# Mörlsara / Code Nexus: Evil Cassandra\nCASSANDRA_MODEL=x\nMorlsara Code Nexus\n'
        changed,rules=transform(original)
        self.assertIn('SagaZ ZeRo', changed)
        self.assertIn('# Mörlsara / Code Nexus: Evil Cassandra', changed)
        self.assertIn('Morlsara Code Nexus', changed)
        self.assertIn('SAGA_MODEL=x', changed)
        self.assertEqual(len(rules),2)

    def test_upstream_is_classified_not_applied(self):
        with tempfile.TemporaryDirectory() as root:
            base=Path(root);up=base/'up';local=base/'local';up.mkdir();local.mkdir()
            (up/'a.txt').write_text('upstream');(local/'a.txt').write_text('custom')
            (up/'b.txt').write_text('same');(local/'b.txt').write_text('same')
            (up/'c.txt').write_text('new')
            result=compare_directories(up,local)
            self.assertEqual({x['category'] for x in result},{'conflict_review_required','identical','upstream_only'})
            self.assertEqual((local/'a.txt').read_text(), 'custom')
            self.assertIn('Nenhuma alteração',markdown(result))

    def test_zip_merge_never_overwrites_or_traverses(self):
        with tempfile.TemporaryDirectory() as root:
            base=Path(root); archive=base/'source.zip';destination=base/'dest';destination.mkdir()
            (destination/'README.md').write_text('LOCAL ORIGINAL')
            with zipfile.ZipFile(archive,'w') as output:
                output.writestr('SagaZ-ZeRo-v3.7.0-zeRo/README.md','MUST NOT REPLACE')
                output.writestr('SagaZ-ZeRo-v3.7.0-zeRo/sagaz/new.py', 'X = 1')
                output.writestr('SagaZ-ZeRo-v3.7.0-zeRo/../outside.txt','UNSAFE')
            preview=stage(archive,destination)
            self.assertTrue(preview['dry_run'])
            self.assertIn('README.md',preview['conflict'])
            self.assertIn('sagaz/new.py',preview['added'])
            self.assertTrue(preview['rejected'])
            self.assertFalse((destination/'sagaz/new.py').exists())
            stage(archive,destination,apply=True)
            self.assertEqual((destination/'README.md').read_text(),'LOCAL ORIGINAL')
            self.assertEqual((destination/'sagaz/new.py').read_text(),'X = 1')
            self.assertFalse((base/'outside.txt').exists())


if __name__=='__main__':
    unittest.main()
