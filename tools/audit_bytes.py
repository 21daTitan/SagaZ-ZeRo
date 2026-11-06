#!/usr/bin/env python3
"""Strict repository source check: UTF-8, LF, no smart quotes or NUL bytes."""
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUFFIXES = {'.py', '.js', '.sh', '.html', '.css', '.json', '.yaml', '.yml', '.toml', '.md'}
SKIP_PARTS = {'.git', '__pycache__', 'node_modules', 'dist', 'projects', 'state', 'exports', 'backups', '.venv'}
INVALID = set('\u2018\u2019\u201c\u201d')


def audit(root=ROOT):
    errors=[]
    inspected=0
    for file in sorted(Path(root).rglob('*')):
        if not file.is_file() or file.suffix.lower() not in SUFFIXES or any(part in SKIP_PARTS for part in file.relative_to(root).parts):
            continue
        if file.is_symlink():
            continue
        inspected+=1
        raw=file.read_bytes()
        try:
            value=raw.decode('utf-8')
        except UnicodeDecodeError:
            errors.append(f'{file.relative_to(root)}: not UTF-8')
            continue
        if b'\x00' in raw:
            errors.append(f'{file.relative_to(root)}: NUL byte')
        if b'\r' in raw:
            errors.append(f'{file.relative_to(root)}: CR byte')
        # Natural-language documentation may use quotes; program source may not.
        if file.suffix.lower() in {'.py', '.js', '.sh'} and any(c in INVALID for c in value):
            errors.append(f'{file.relative_to(root)}: smart quotation mark in source')
    return inspected,errors


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--strict',action='store_true')
    args=parser.parse_args()
    count,errors=audit()
    print(f'[audit_bytes] examined={count} errors={len(errors)}')
    for error in errors[:100]:print('[FAIL]',error)
    return 1 if errors and args.strict else 0

if __name__=='__main__':
    raise SystemExit(main())
