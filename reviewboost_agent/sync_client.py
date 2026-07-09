"""HTTP client for Review Boost edge functions."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import httpx

@dataclass
class SyncConfigResponse:
    enabled: bool
    interval_minutes: int
    table_name: str
    col_code: str
    col_lastname: str
    col_firstname: str
    col_phone1: str
    col_phone2: str
    col_email: Optional[str]
    manual_trigger_requested_at: Optional[str]
    last_seen_max_code: Optional[str]

class SyncClient:
    def __init__(self, api_base: str, api_key: str, timeout: float = 20.0) -> None:
        self._api_base = api_base.rstrip('/')
        self._headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'ReviewBoostAgent/1.0',
        }
        self._timeout = timeout

    def get_config(self) -> SyncConfigResponse:
        url = f'{self._api_base}/functions/v1/mdb-sync-config'
        with httpx.Client(timeout=self._timeout) as c:
            r = c.get(url, headers=self._headers)
            r.raise_for_status()
            data = r.json()

        table_name = (data.get('table_name') or '').strip()
        if not table_name:
            raise RuntimeError('Review Boost no devolvió table_name. Revisa el mapeo MDB en la app.')

        col_code = (data.get('col_code') or '').strip()
        col_lastname = (data.get('col_lastname') or '').strip()
        col_firstname = (data.get('col_firstname') or '').strip()
        col_phone1 = (data.get('col_phone1') or '').strip()
        col_phone2 = (data.get('col_phone2') or '').strip()
        missing = [name for name, value in {
            'col_code': col_code,
            'col_lastname': col_lastname,
            'col_firstname': col_firstname,
            'col_phone1': col_phone1,
            'col_phone2': col_phone2,
        }.items() if not value]
        if missing:
            raise RuntimeError('Mapeo MDB incompleto en Review Boost: ' + ', '.join(missing))

        return SyncConfigResponse(
            enabled=bool(data.get('enabled')),
            interval_minutes=int(data.get('interval_minutes') or 60),
            table_name=table_name,
            col_code=col_code,
            col_lastname=col_lastname,
            col_firstname=col_firstname,
            col_phone1=col_phone1,
            col_phone2=col_phone2,
            col_email=(data.get('col_email') or None),
            manual_trigger_requested_at=data.get('manual_trigger_requested_at'),
            last_seen_max_code=data.get('last_seen_max_code'),
        )

    def ingest(self, rows: list[dict], trigger: str) -> dict:
        url = f'{self._api_base}/functions/v1/mdb-sync-ingest'
        with httpx.Client(timeout=self._timeout) as c:
            r = c.post(url, headers=self._headers, json={'trigger': trigger, 'rows': rows})
            r.raise_for_status()
            return r.json()
