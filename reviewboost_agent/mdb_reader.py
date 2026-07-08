"""Read patients from password-protected Access MDB via ODBC."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterator, Optional

try:
    import pyodbc  # type: ignore
except ImportError:
    pyodbc = None  # type: ignore

@dataclass
class ColumnMap:
    table_name: str
    col_code: str
    col_lastname: str
    col_firstname: str
    col_phone1: str
    col_phone2: str
    col_email: Optional[str] = None

@dataclass
class PatientRow:
    patient_id: str
    last_name: str
    first_name: str
    phone1: str
    phone2: str
    email: Optional[str]

    def to_payload(self) -> dict:
        return {
            'patient_id': self.patient_id,
            'last_name': self.last_name,
            'first_name': self.first_name,
            'phone1': self.phone1,
            'phone2': self.phone2,
            'email': self.email,
        }

def _connect(mdb_path: str, password: str):
    if pyodbc is None:
        raise RuntimeError('pyodbc no está instalado')
    driver = '{Microsoft Access Driver (*.mdb, *.accdb)}'
    conn_str = f'DRIVER={driver};DBQ={mdb_path};'
    if password:
        conn_str += f'PWD={password};'
    return pyodbc.connect(conn_str, autocommit=True, readonly=True)

def test_connection(mdb_path: str, password: str, table_name: str = 'Pacientes') -> int:
    with _connect(mdb_path, password) as conn:
        cur = conn.cursor()
        cur.execute(f'SELECT COUNT(*) FROM [{table_name}]')
        return int(cur.fetchone()[0])

def read_new_patients(mdb_path: str, password: str, cols: ColumnMap, since_code: Optional[str], batch_size: int = 500) -> Iterator[list[PatientRow]]:
    select_cols = [cols.col_code, cols.col_lastname, cols.col_firstname, cols.col_phone1, cols.col_phone2]
    if cols.col_email:
        select_cols.append(cols.col_email)
    cols_sql = ', '.join(f'[{c}]' for c in select_cols)
    sql = f'SELECT {cols_sql} FROM [{cols.table_name}]'
    params: list = []
    if since_code:
        sql += f' WHERE [{cols.col_code}] > ?'
        params.append(since_code)
    sql += f' ORDER BY [{cols.col_code}]'
    with _connect(mdb_path, password) as conn:
        cur = conn.cursor()
        cur.execute(sql, params)
        batch: list[PatientRow] = []
        while True:
            rows = cur.fetchmany(batch_size)
            if not rows:
                break
            for r in rows:
                batch.append(PatientRow(
                    patient_id=str(r[0]).strip() if r[0] is not None else '',
                    last_name=(r[1] or '').strip(),
                    first_name=(r[2] or '').strip(),
                    phone1=(r[3] or '').strip(),
                    phone2=(r[4] or '').strip(),
                    email=(r[5] or '').strip() if cols.col_email and len(r) > 5 else None,
                ))
                if len(batch) >= batch_size:
                    yield batch
                    batch = []
        if batch:
            yield batch