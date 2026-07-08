"""Entrypoint dispatcher.

Modes:
  --service              Launched by Windows SCM; hands off to service dispatcher.
  --install-service      Register/refresh the Windows service (requires admin).
  --uninstall-service    Stop and remove the Windows service (requires admin).
  --start-service        Start the installed service.
  --stop-service         Stop the installed service.
  --run-once [--force]   Execute one sync cycle in-process (diagnostics).
  --diagnostics          Print diagnostics JSON to stdout.
  (no args)              Open configuration wizard + tray.
"""
from __future__ import annotations
import json
import sys


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
            print(f'installed, start failed: {exc}', file=sys.stderr)
            return 2
        print('ok')
        return 0

    if '--uninstall-service' in args:
        from reviewboost_agent.service import uninstall_service
        uninstall_service()
        print('ok')
        return 0

    if '--start-service' in args:
        from reviewboost_agent.service import start_service
        start_service()
        print('ok')
        return 0

    if '--stop-service' in args:
        from reviewboost_agent.service import stop_service
        stop_service()
        print('ok')
        return 0

    if '--run-once' in args:
        from reviewboost_agent.scheduler import run_once
        run_once(force='--force' in args)
        return 0

    if '--diagnostics' in args:
        from reviewboost_agent.diagnostics import collect_diagnostics
        print(json.dumps(collect_diagnostics(), indent=2, ensure_ascii=False, default=str))
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