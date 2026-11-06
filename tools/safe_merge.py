#!/usr/bin/env python3
"""Safely import ZIP contents without overwriting any existing file."""
import argparse
import json
from pathlib import Path, PurePosixPath
import shutil
import stat
import zipfile

EXCLUDED={'.git', 'node_modules', '__pycache__', 'state', 'projects', 'dist', 'exports', 'backups'}
MAX_BYTES = 250_000_000


def stage(source, destination, apply=False):
    destination=Path(destination).resolve()
    destination.mkdir(parents=True,exist_ok=True)
    result={'added':[], 'conflict':[], 'rejected':[], 'dry_run':not apply}
    total=0
    with zipfile.ZipFile(source) as archive:
        names=archive.infolist()
        prefix = 'SagaZ-ZeRo-v3.7.0-zeRo/' if any(row.filename.startswith('SagaZ-ZeRo-v3.7.0-zeRo/') for row in names) else ''
        for entry in names:
            if entry.is_dir():
                continue
            filename=entry.filename
            if prefix and filename.startswith(prefix):
                filename=filename[len(prefix):]
            parts=PurePosixPath(filename).parts
            if (not filename or filename.startswith('/') or '\\' in filename or
                '..' in parts or any(x in EXCLUDED for x in parts) or filename=='.env' or
                filename.startswith('.env.') and filename!='.env.example' or
                stat.S_ISLNK(entry.external_attr >> 16)):
                result['rejected'].append(filename)
                continue
            total += entry.file_size
            if total>MAX_BYTES:
                raise ValueError('Archive expands beyond size limit')
            target=destination.joinpath(*parts)
            if not target.resolve().is_relative_to(destination):
                result['rejected'].append(filename)
            elif target.exists() or target.is_symlink():
                result['conflict'].append(filename)
            else:
                result['added'].append(filename)
                if apply:
                    target.parent.mkdir(parents=True,exist_ok=True)
                    with archive.open(entry) as stream, target.open('xb') as output:
                        shutil.copyfileobj(stream, output)
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('zip_file')
    parser.add_argument('destination')
    parser.add_argument('--apply', action='store_true',help='Import new paths only; never replace existing paths')
    a=parser.parse_args()
    print(json.dumps(stage(a.zip_file,a.destination,a.apply),indent=2,ensure_ascii=False))

if __name__=='__main__':
    main()
