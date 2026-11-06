import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

REPO=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('dsant',REPO/'dsant.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class SetupTests(unittest.TestCase):
    def test_install_idempotent_and_isolated(self):
        with tempfile.TemporaryDirectory() as td:
            first=m.install('all','core',td)
            self.assertEqual(len(first['updated']),9)
            self.assertEqual(m.install('all','core',td)['updated'],[])
            self.assertFalse((Path(td)/'.env').exists())
            self.assertFalse((Path(td)/'.claude/skills/dsant-creator-cartoon').exists())

    def test_conflict_and_edits_preserved(self):
        with tempfile.TemporaryDirectory() as td:
            dst=Path(td)/'.claude/skills/dsant-creator';dst.mkdir(parents=True)
            (dst/'personal.txt').write_text('keep')
            with self.assertRaises(ValueError):m.install('all','core',td)
            self.assertEqual((dst/'personal.txt').read_text(),'keep')
            self.assertFalse((Path(td)/'.agents/skills/dsant-creator').exists())
        with tempfile.TemporaryDirectory() as td:
            m.install('claude','core',td)
            dst=Path(td)/'.claude/skills/dsant-creator/SKILL.md';dst.write_text('my edits')
            with self.assertRaises(ValueError):m.install('claude','core',td)
            self.assertEqual(dst.read_text(),'my edits')

    def test_version_change_keeps_backup(self):
        with tempfile.TemporaryDirectory() as td:
            fixture=Path(td)/'skills';shutil.copytree(m.SKILLS,fixture)
            home=Path(td)/'home'
            with patch.object(m,'SKILLS',fixture):
                m.install('codex','core',home)
                (fixture/'dsant-creator/SKILL.md').write_text('updated')
                m.install('codex','core',home)
            backups=list((home/'.agents/skills').glob('.dsant-creator.backup-*'))
            self.assertEqual(len(backups),1)
            self.assertIn('name: dsant-creator',(backups[0]/'SKILL.md').read_text(encoding='utf-8'))

    def test_pack_scope_and_exclusive_write(self):
        with tempfile.TemporaryDirectory() as td:
            dst=Path(td)/'pack.md';m.pack(dst)
            self.assertNotIn('"scope": "hot"',dst.read_text(encoding='utf-8'))
            with self.assertRaises(FileExistsError):m.pack(dst)
            hot=Path(td)/'hot.md';m.pack(hot,'hot')
            self.assertIn('"scope": "hot"',hot.read_text(encoding='utf-8'))

    def test_package_integrity(self):
        self.assertEqual(len(list(m.SKILLS.glob('*/SKILL.md'))),6)
        for skill in m.SKILLS.iterdir():
            self.assertIn('name: '+skill.name,(skill/'SKILL.md').read_text(encoding='utf-8'))
        self.assertTrue(m.doctor()['core_ready'])

    def test_update_local_git_and_dirty_refusal(self):
        with tempfile.TemporaryDirectory() as td:
            base=Path(td);origin=base/'origin.git';source=base/'source';clone=base/'clone';home=base/'home'
            def git(*args,cwd=None):
                return subprocess.run(['git',*args],cwd=cwd,check=True,capture_output=True,text=True)
            git('init','--bare',str(origin));source.mkdir();git('init',cwd=source)
            git('config','user.name','Test',cwd=source);git('config','user.email','test@example.invalid',cwd=source)
            shutil.copy2(REPO/'dsant.py',source/'dsant.py');shutil.copy2(REPO/'VERSION',source/'VERSION')
            shutil.copytree(m.SKILLS,source/'.agents/skills',ignore=shutil.ignore_patterns('__pycache__'))
            git('add','.',cwd=source);git('commit','-m','initial',cwd=source);git('remote','add','origin',str(origin),cwd=source);git('push','-u','origin','HEAD',cwd=source)
            git('clone',str(origin),str(clone))
            (source/'VERSION').write_text('9.9.9-test')
            git('add','VERSION',cwd=source);git('commit','-m','next version',cwd=source);git('push',cwd=source)
            with patch.object(m,'ROOT',clone),patch.object(m,'REMOTE',str(origin)):
                result=m.update('claude','core',home)
                self.assertNotEqual(result['before'],result['after'])
                self.assertEqual((clone/'VERSION').read_text(),'9.9.9-test')
                (clone/'VERSION').write_text('modified')
                with self.assertRaises(ValueError):m.update('claude','core',home)

# Load the existing core tests against the packaged, portable source.
spec2=importlib.util.spec_from_file_location('core_tests',REPO/'.agents/skills/dsant-creator/scripts/test_creator.py')
core=importlib.util.module_from_spec(spec2);spec2.loader.exec_module(core)
CreatorTests=core.CreatorTests

if __name__=='__main__':unittest.main()
