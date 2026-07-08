"""Entrypoint: --service, --run-once, or default (wizard + tray)."""
from __future__ import annotations
import sys

def main(argv: list[str]) -> int:
    args = set(argv[1:])
    if '--service' in args:
        from .scheduler import run_forever
        run_forever()
        return 0
    if '--run-once' in args:
        from .scheduler import run_once
        run_once(force='--force' in args)
        return 0
    from .config import load_config
    from .setup_wizard import open_wizard
    from .tray import run_tray
    cfg = load_config()
    if not cfg.is_ready():
        open_wizard()
    run_tray()
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))