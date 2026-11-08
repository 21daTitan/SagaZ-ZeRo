"""Offline checks for SagaZ operator provider settings and CTI commands."""
from pathlib import Path
import os
import stat
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from sagaz.provider_config import save, load, validate


class ProviderConfigTests(unittest.TestCase):
    def test_remote_requires_https_and_key(self):
        for base, model, key in [
            ('http://api.example/v1', 'm', 'abc'),
            ('https://api.example/v1', 'm', ''),
            ('https://api.example/bad', 'm', 'abc'),
        ]:
            with self.assertRaises(ValueError):
                validate(base, model, key)

    def test_local_allows_missing_key(self):
        validate('http://127.0.0.1:11434/v1', 'local', '')

    def test_private_file_and_load(self):
        with tempfile.TemporaryDirectory() as tmp:
            config = Path(tmp)/'provider.json'
            with patch.dict(os.environ, {'SAGAZ_PROVIDER_FILE':str(config)}, clear=True):
                save('http://127.0.0.1:11434/v1', 'offline-test')
                self.assertEqual(stat.S_IMODE(config.stat().st_mode), 0o600)
                for name in ('DSANT_BASE_URL', 'DSANT_MODEL', 'DSANT_API_KEY'):
                    os.environ.pop(name, None)
                self.assertTrue(load())
                self.assertEqual(os.environ['DSANT_MODEL'], 'offline-test')

    def test_insecure_mode_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            config = Path(tmp)/'provider.json'
            with patch.dict(os.environ, {'SAGAZ_PROVIDER_FILE':str(config)}, clear=True):
                save('http://localhost:11434/v1', 'local')
                config.chmod(0o644)
                with self.assertRaises(ValueError):
                    load()

class OperatorIntegrationTests(unittest.TestCase):
    def test_unknown_slash_is_not_creative_task(self):
        from sagaz.services import operator_command
        result = operator_command('/skilld')
        self.assertEqual(result['mode'], 'command')
        self.assertIn('desconhecido', result['answer'].lower())

    def test_llm_chat_persists_and_resumes(self):
        from sagaz.ai_session import respond
        with tempfile.TemporaryDirectory() as tmp:
            fake = MagicMock()
            fake.chat.side_effect = [
                {'choices': [{'message': {'content': 'PONG'}}]},
                {'choices': [{'message': {'content': 'Resposta 2'}}]},
            ]
            with patch('sagaz.ai_session.Gateway', return_value=fake):
                first = respond('teste', state_root=Path(tmp))
                second = respond('continue', state_root=Path(tmp), parent_id=first['id'])
            self.assertEqual(first['answer'], 'PONG')
            self.assertEqual(second['answer'], 'Resposta 2')
            self.assertEqual(len(fake.chat.call_args.args[1]['messages']), 4)
            self.assertTrue((Path(tmp)/second['id']/'conversation.json').is_file())

if __name__ == '__main__':
    unittest.main()
