import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

P=Path(__file__).resolve().parents[1]/'.agents/skills/remotion-problem-resolve-video/scripts/voiceover.py'
s=importlib.util.spec_from_file_location('voice',P);v=importlib.util.module_from_spec(s);s.loader.exec_module(v)

class VoiceCostTests(unittest.TestCase):
    def test_paid_requires_explicit_flag(self):
        with patch('sys.argv',['voiceover','--lines','absent.json','--voice','id','--provider','elevenlabs']),patch.object(v,'eleven_request') as request:
            with self.assertRaises(SystemExit) as result:v.main()
            self.assertEqual(result.exception.code,2);request.assert_not_called()

    def test_default_stays_free_even_with_key(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);(p/'lines.json').write_text('{"s1":"teste"}')
            async def fake_edge(*args):return [{'text':'teste','start':0,'end':1}]
            with patch('sys.argv',['voiceover','--lines',str(p/'lines.json'),'--voice','pt-BR-AntonioNeural']),patch.object(v,'OUT_AUDIO',p/'audio'),patch.object(v,'OUT_JSON',p/'timings.json'),patch.object(v,'env_key',return_value='configured-key') as key,patch.object(v,'synth_edge',side_effect=fake_edge),patch.object(v,'synth_eleven') as paid:
                v.main();key.assert_not_called();paid.assert_not_called()

if __name__=='__main__':unittest.main()
