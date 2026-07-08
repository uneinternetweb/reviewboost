"""Collect diagnostics info and run end-to-end checks."""
from __future__ import annotations

import os
import platform
import socket
import sys
from dataclasses import dataclass
from datetime import datetime, timezone

from . import __version__
from .config import load_config
from .logger import get_logger
from .service import service_exists, service_status, SERVICE_NAME

log = get_logger('diagnostics')


@dataclass
class CheckResult:
    name: str
    ok: bool
    detail: str = ''


def _exe_path() -> str:
    return os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else sys.argv[0])


def collect_diagnostics() -> dict:
    cfg = load_config()
    return {
        'agent_version': __version__,
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'host': socket.gethostname(),
        'os': f'{platform.system()} {platform.release()} ({platform.version()})',
        'python': sys.version,
        'executable': _exe_path(),
        'config_ready': cfg.is_ready(),
        'mdb_path': cfg.mdb_path,
        'mdb_password_set': bool(cfg.mdb_password),
        'agent_key_set': bool(cfg.agent_api_key),
        'api_base': cfg.api_base,
        'service_name': SERVICE_NAME,
        'service_installed': service_exists(),
        'service_status': service_status(),
        'last_run_at': cfg.last_run_at,
        'last_sync_ok_at': cfg.last_sync_ok_at,
        'last_supabase_ok_at': cfg.last_supabase_ok_at,
        'last_seen_manual_trigger': cfg.last_seen_manual_trigger,
        'last_error': cfg.last_error,
        'last_error_at': cfg.last_error_at,
    }


def run_full_check() -> list[CheckResult]:
    results: list[CheckResult] = []
    cfg = load_config()

    installed = service_exists()
    results.append(CheckResult('Servicio instalado', installed,
                               'Ejecuta "Reinstalar servicio"' if not installed else SERVICE_NAME))

    status = service_status()
    results.append(CheckResult('Servicio iniciado', status == 'running', f'Estado: {status}'))

    if not cfg.is_ready():
        results.append(CheckResult('Configuración válida', False, 'Faltan MDB o clave del agente.'))
        return results

    try:
        from .sync_client import SyncClient
        client = SyncClient(cfg.api_base, cfg.agent_api_key)
        remote = client.get_config()
        results.append(CheckResult('Conexión con Supabase', True,
                                   f'enabled={remote.enabled}, interval={remote.interval_minutes} min'))
    except Exception as exc:
        results.append(CheckResult('Conexión con Supabase', False, str(exc)))
        return results

    try:
        from .mdb_reader import test_connection
        count = test_connection(cfg.mdb_path, cfg.mdb_password, remote.table_name)
        results.append(CheckResult('Conexión con MDB', True, cfg.mdb_path))
        results.append(CheckResult('Tabla encontrada', True,
                                   f'{remote.table_name} ({count} registros)'))
    except Exception as exc:
        results.append(CheckResult('Conexión con MDB', False, str(exc)))
        return results

    results.append(CheckResult('Configuración válida', True,
                               'Todos los pasos correctos.'))
    return results


def format_report() -> str:
    import json
    lines = ['=== Review Boost Agent — Informe de diagnóstico ===', '']
    info = collect_diagnostics()
    for k, v in info.items():
        lines.append(f'{k}: {v}')
    lines.append('')
    lines.append('=== Comprobaciones ===')
    for r in run_full_check():
        icon = '[OK]' if r.ok else '[FAIL]'
        lines.append(f'{icon} {r.name} — {r.detail}')
    lines.append('')
    lines.append('=== JSON ===')
    lines.append(json.dumps(info, indent=2, ensure_ascii=False, default=str))
    return '\n'.join(lines)
