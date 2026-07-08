"""Rotating logger."""
from __future__ import annotations
import logging, os
from logging.handlers import RotatingFileHandler
from pathlib import Path

def _log_dir() -> Path:
    base = os.environ.get('LOCALAPPDATA') or os.path.expanduser('~')
    p = Path(base) / 'ReviewBoost' / 'logs'
    p.mkdir(parents=True, exist_ok=True)
    return p

def get_logger(name: str = 'reviewboost') -> logging.Logger:
    lg = logging.getLogger(name)
    if lg.handlers:
        return lg
    lg.setLevel(logging.INFO)
    fmt = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
    fh = RotatingFileHandler(_log_dir() / 'agent.log', maxBytes=1_000_000, backupCount=5, encoding='utf-8')
    fh.setFormatter(fmt); lg.addHandler(fh)
    sh = logging.StreamHandler(); sh.setFormatter(fmt); lg.addHandler(sh)
    return lg