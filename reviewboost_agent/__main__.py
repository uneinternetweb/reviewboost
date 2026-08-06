"""Entrypoint dispatcher for the Review Boost Windows agent."""
from __future__ import annotations

import json
import sys
from pathlib import Path


def _write_visible_report(name: str, text: str) -> Path:
    from reviewboost_agent.logger import log_dir

    path = log_dir() / name
    path.write_text(text, encoding='utf-8')
    try:
        import ctypes
        ctypes.windll.user32.MessageBoxW(
            0,
            f'Informe guardado en:\n{path}',
            'Review Boost Agent',
            0x40,
        )
    except Exception:
        pass
    return path


def main(argv: list[str]) -> int:
    args = set(argv[1:])

    if '--service' in args:
        from reviewboost_agent.service import run_service_dispatch
        run_service_dispatch()
        return 0

    if '--install-service' in args:
        from reviewboost_agent.service import install_service, start_service
        install_service()
        try:
            start_service()
        except Exception as exc:
            _write_visible_report('install-error.txt', f'installed, start failed: {exc}')
            return 2
        return 0

    if '--uninstall-service' in args:
        from reviewboost_agent.service import uninstall_service
        uninstall_service()
        return 0

    if '--start-service' in args:
        from reviewboost_agent.service import start_service
        start_service()
        return 0

    if '--stop-service' in args:
        from reviewboost_agent.service import stop_service
        stop_service()
        return 0

    if '--run-once' in args:
        from reviewboost_agent.scheduler import run_once
        from reviewboost_agent.logger import log_path
        try:
            run_once(force='--force' in args)
            _write_visible_report(
                'run-once-result.txt',
                f'Ejecución manual terminada correctamente.\nLog: {log_path()}',
            )
            return 0
        except Exception as exc:
            _write_visible_report(
                'run-once-error.txt',
                f'{type(exc).__name__}: {exc}\nLog: {log_path()}',
            )
            return 1

    if '--diagnostics' in args:
        from reviewboost_agent.diagnostics import format_report
        report = format_report()
        _write_visible_report('diagnostics.txt', report)
        return 0

    from reviewboost_agent.config import load_config
    from reviewboost_agent.setup_wizard import open_wizard
    from reviewboost_agent.tray import run_tray

    cfg = load_config()
    if not cfg.is_ready():
        open_wizard()
    run_tray()
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
