"""Per-user provider configuration; never write credentials to the Git repository."""
from __future__ import annotations
import json
import os
from pathlib import Path
import stat
import tempfile
from urllib.parse import urlsplit

ENV_NAMES = ('DSANT_BASE_URL', 'DSANT_MODEL', 'DSANT_API_KEY')


def path() -> Path:
    custom = os.environ.get('SAGAZ_PROVIDER_FILE')
    return Path(custom).expanduser() if custom else Path.home() / '.config' / 'sagaz-zero' / 'provider.json'


def validate(base: str, model: str, key: str = '') -> None:
    if not isinstance(base, str) or not isinstance(model, str) or not isinstance(key, str):
        raise ValueError('Configuração inválida')
    base = base.strip().rstrip('/')
    model = model.strip()
    url = urlsplit(base)
    local = url.hostname in ('localhost', '127.0.0.1', '::1')
    if not base or not model or len(model) > 250 or '\n' in model:
        raise ValueError('Informe endpoint e modelo')
    if not (url.scheme == 'https' or (url.scheme == 'http' and local)):
        raise ValueError('Use HTTPS ou HTTP somente em localhost')
    if not url.netloc or url.username or url.password or url.query or url.fragment or not url.path.endswith('/v1'):
        raise ValueError('A URL deve terminar com /v1 e não pode conter credenciais')
    if not local and not key:
        raise ValueError('Provedores remotos exigem uma chave API')
    if '\n' in key or '\r' in key:
        raise ValueError('Chave API inválida')


def load() -> bool:
    cfg = path()
    if not cfg.exists():
        return False
    if cfg.is_symlink():
        raise ValueError('Arquivo de configuração não pode ser um link')
    details = cfg.stat()
    if details.st_uid != os.getuid() or stat.S_IMODE(details.st_mode) & 0o077:
        raise ValueError('Configuração do provedor precisa pertencer ao usuário e ter permissão 0600')
    data = json.loads(cfg.read_text(encoding='utf-8'))
    if not isinstance(data, dict):
        raise ValueError('Configuração do provedor inválida')
    base, model, key = (data.get('base_url', ''), data.get('model', ''), data.get('api_key', ''))
    validate(base, model, key)
    values = dict(zip(ENV_NAMES, (base.strip().rstrip('/'), model.strip(), key)))
    for name, value in values.items():
        if not os.environ.get(name):
            os.environ[name] = value
    return True


def save(base: str, model: str, key: str = '') -> Path:
    validate(base, model, key)
    cfg = path()
    cfg.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    if cfg.is_symlink():
        raise ValueError('Configuração existente não pode ser link')
    contents = json.dumps({'base_url': base.strip().rstrip('/'), 'model': model.strip(), 'api_key': key}, ensure_ascii=False)
    fd, tmp = tempfile.mkstemp(prefix='.provider-', dir=cfg.parent)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            stream.write(contents + '\n')
        os.replace(tmp, cfg)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    for name, value in zip(ENV_NAMES, (base.strip().rstrip('/'), model.strip(), key)):
        os.environ[name] = value
    return cfg
