#!/usr/bin/env python3
"""Generate source ZIP and SHA256; excludes workspaces, .git, credentials and caches."""
import hashlib
from pathlib import Path
import zipfile

ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT.parent/'dist-sagaz'
SKIP={'.git','.venv','__pycache__','node_modules','projects','state','exports','backups','dist'}


def pack():
    version=(ROOT/'VERSION').read_text().strip()
    if version!='3.7.0-zeRo':raise ValueError('Not the expected version')
    DIST.mkdir(parents=True,exist_ok=True)
    path=DIST/f'SagaZ-ZeRo-{version}.zip'
    count=0
    with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=8) as archive:
        for file in sorted(ROOT.rglob('*')):
            if not file.is_file() or file.is_symlink() or any(part in SKIP for part in file.relative_to(ROOT).parts):
                continue
            if file.name=='.env' or (file.name.startswith('.env.') and file.name!='.env.example') or file.suffix in ('.pyc','.pyo','.log'):
                continue
            info=zipfile.ZipInfo(f'{ROOT.name}/{file.relative_to(ROOT).as_posix()}',date_time=(2026,11,5,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=(0o100755 if file.stat().st_mode & 0o111 else 0o100644)<<16
            archive.writestr(info,file.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=8)
            count+=1
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    sums=DIST/'SHA256SUMS'
    sums.write_text(f'{digest}  {path.name}\n',encoding='ascii')
    return path,count,digest

if __name__=='__main__':
    file,count,sha=pack()
    print(f'ZIP: {file}\nfiles: {count}\nSHA256: {sha}')
