"""Encrypted agent configuration using Windows DPAPI (LOCAL_MACHINE scope)."""
from __future__ import annotations
import json, os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional

try:
    import win32crypt  # type: ignore
    _HAS_DPAPI = True
except ImportError:
    _HAS_DPAPI = False

CRYPTPROTECT_LOCAL_MACHINE = 0x4

def _config_path() -> Path:
    base = os.environ.get('PROGRAMDATA') or os.path.expanduser('~')
    p = Path(base) / 'ReviewBoost'
    p.mkdir(parents=True, exist_ok=True)
    return p / 'config.dat'

@dataclass
class AgentConfig:
    api_base: str = 'https://fbrvtnpxknqxioizduqk.supabase.co'
    mdb_path: str = ''
    mdb_password: str = ''
    agent_api_key: str = ''
    last_run_at: Optional[str] = None
    last_seen_manual_trigger: Optional[str] = None

    def is_ready(self) -> bool:
        return bool(self.mdb_path and self.agent_api_key)

def _encrypt(data: bytes) -> bytes:
    if not _HAS_DPAPI:
        return b'PLAIN:' + data
    return win32crypt.CryptProtectData(data, 'ReviewBoostAgent', None, None, None, CRYPTPROTECT_LOCAL_MACHINE)

def _decrypt(blob: bytes) -> bytes:
    if blob.startswith(b'PLAIN:'):
        return blob[len(b'PLAIN:'):]
    if not _HAS_DPAPI:
        raise RuntimeError('DPAPI not available')
    _desc, data = win32crypt.CryptUnprotectData(blob, None, None, None, 0)
    return data

def load_config() -> AgentConfig:
    p = _config_path()
    if not p.exists():
        return AgentConfig()
    payload = json.loads(_decrypt(p.read_bytes()).decode('utf-8'))
    return AgentConfig(**payload)

def save_config(cfg: AgentConfig) -> None:
    p = _config_path()
    p.write_bytes(_encrypt(json.dumps(asdict(cfg)).encode('utf-8')))
    try:
        os.chmod(p, 0o600)
    except OSError:
        pass