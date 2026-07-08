"""Main sync loop."""
from __future__ import annotations
import time
from datetime import datetime, timezone
from typing import Optional

from .config import AgentConfig, load_config, save_config
from .logger import get_logger
from .mdb_reader import ColumnMap, read_new_patients
from .sync_client import SyncClient, SyncConfigResponse

log = get_logger('scheduler')
POLL_SECONDS = 60

def _parse_iso(v: Optional[str]) -> Optional[datetime]:
    if not v:
        return None
    try:
        return datetime.fromisoformat(v.replace('Z', '+00:00'))
    except ValueError:
        return None

def _should_run(cfg: AgentConfig, remote: SyncConfigResponse) -> tuple[bool, str]:
    manual = remote.manual_trigger_requested_at
    if manual and manual != cfg.last_seen_manual_trigger:
        return True, 'manual'
    last_local = _parse_iso(cfg.last_run_at)
    if last_local is None:
        return True, 'scheduled'
    age_min = (datetime.now(timezone.utc) - last_local).total_seconds() / 60
    if age_min >= remote.interval_minutes:
        return True, 'scheduled'
    return False, ''

def run_once(force: bool = False) -> None:
    cfg = load_config()
    if not cfg.is_ready():
        log.warning('Config incompleta; abre el asistente.')
        return
    client = SyncClient(cfg.api_base, cfg.agent_api_key)
    remote = client.get_config()
    if not remote.enabled:
        log.info('Sincronización deshabilitada por el servidor.')
        return
    should, trigger = (True, 'manual') if force else _should_run(cfg, remote)
    if not should:
        return
    cols = ColumnMap(
        table_name=remote.table_name,
        col_code=remote.col_code,
        col_lastname=remote.col_lastname,
        col_firstname=remote.col_firstname,
        col_phone1=remote.col_phone1,
        col_phone2=remote.col_phone2,
        col_email=remote.col_email,
    )
    log.info('Sync inicio trigger=%s since=%s', trigger, remote.last_seen_max_code)
    total = 0
    for batch in read_new_patients(cfg.mdb_path, cfg.mdb_password, cols, remote.last_seen_max_code):
        payload = [r.to_payload() for r in batch]
        result = client.ingest(payload, trigger=trigger)
        total += len(payload)
        log.info('Batch %d filas resp=%s', len(payload), result)
    cfg.last_run_at = datetime.now(timezone.utc).isoformat()
    cfg.last_seen_manual_trigger = remote.manual_trigger_requested_at
    save_config(cfg)
    log.info('Sync fin total=%d', total)

def run_forever() -> None:
    log.info('Agente Review Boost iniciado (servicio).')
    while True:
        try:
            run_once()
        except Exception as exc:
            log.exception('Error ciclo: %s', exc)
        time.sleep(POLL_SECONDS)