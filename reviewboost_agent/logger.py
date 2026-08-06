"""Rotating logger shared by interactive mode and the Windows service."""
from __future__ import annotations

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path


def log_dir() -> Path:
    """Return a machine-wide log directory visible to admins and LocalSystem."""
    base = os.environ.get('PROGRAMDATA') or r'C:\ProgramData'
    path = Path(base) / 'ReviewBoost' / 'logs'
    path.mkdir(parents=True, exist_ok=True)
    return path


def log_path() -> Path:
    return log_dir() / 'agent.log'


def get_logger(name: str = 'reviewboost') -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    logger.propagate = False
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] pid=%(process)d %(name)s: %(message)s'
    )

    file_handler = RotatingFileHandler(
        log_path(), maxBytes=2_000_000, backupCount=5, encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Useful during development and console builds. Harmless in windowed builds.
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    return logger
