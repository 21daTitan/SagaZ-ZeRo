import asyncio
import json
import tempfile
import unittest
from pathlib import Path

from sagaz.discord_memory import DiscordMemory
from sagaz.god import DEUS, DEVOTIONAL, is_destructive_command, resolve


class GodAndDiscordTests(unittest.TestCase):
    def test_profile_resolution_keeps_destructive_confirmation(self):
        self.assertIs(resolve('deus'), DEUS)
        self.assertIs(resolve('off'), DEVOTIONAL)
        self.assertTrue(DEUS.confirm_destructive)
        self.assertTrue(is_destructive_command('rm -rf /tmp/test'))
        self.assertTrue(is_destructive_command('sudo systemctl restart sagaz'))
        self.assertFalse(is_destructive_command('git status'))

    def test_discord_memory_requires_consent_and_supports_stats_search(self):
        with tempfile.TemporaryDirectory() as directory:
            memory = DiscordMemory(Path(directory) / 'discord.sqlite3')
            rows = [{'id': '1', 'channel_id': 'ops', 'author_id': 'u1', 'author_name': 'Ana',
                     'content': 'Deploy SagaZ depois dos testes', 'timestamp': '2026-11-07T10:00:00+00:00'}]
            with self.assertRaises(PermissionError):
                memory.ingest(rows)
            self.assertEqual(memory.ingest(rows, consent=True), 1)
            self.assertEqual(memory.summary()['messages'], 1)
            self.assertEqual(memory.search('SagaZ')['count'], 1)
            self.assertIn('Ana', memory.context('Deploy'))


if __name__ == '__main__':
    unittest.main()
