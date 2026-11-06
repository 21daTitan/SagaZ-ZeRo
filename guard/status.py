"""Report guard status, never silently start or persist a miner."""
from dataclasses import asdict
from guard.config import load

def status():
    result = asdict(load())
    result['running'] = False
    result['installer_available'] = False
    result['note'] = 'Recurso desabilitado. Nenhum minerador ou servico de persistencia distribuido.'
    return result
