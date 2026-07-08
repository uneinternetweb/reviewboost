"""Native Windows service via pywin32 + SCM install/remove helpers.

No NSSM required. The frozen PyInstaller exe is registered directly as the
service binary, invoked with ``--service``. When Windows SCM starts the
process we hand control to ``servicemanager`` which calls ``SvcDoRun``.
"""
from __future__ import annotations

import os
import sys
import time
import threading

SERVICE_NAME = 'ReviewBoostAgent'
SERVICE_DISPLAY = 'Review Boost Agent'
SERVICE_DESCRIPTION = 'Sincroniza pacientes del MDB de Drtooth con Review Boost.'

try:  # pragma: no cover - Windows only
    import win32service
    import win32serviceutil
    import win32event
    import servicemanager
    _HAS_WIN32 = True
except ImportError:  # non-Windows / dev
    _HAS_WIN32 = False


def _exe_path() -> str:
    """Absolute path to the running agent executable (frozen or python)."""
    if getattr(sys, 'frozen', False):
        return os.path.abspath(sys.executable)
    return f'"{sys.executable}" -m reviewboost_agent'


def _open_scm(access: int):
    return win32service.OpenSCManager(None, None, access)


def service_exists() -> bool:
    if not _HAS_WIN32:
        return False
    try:
        scm = _open_scm(win32service.SC_MANAGER_CONNECT)
    except Exception:
        return False
    try:
        try:
            h = win32service.OpenService(scm, SERVICE_NAME, win32service.SERVICE_QUERY_STATUS)
            win32service.CloseServiceHandle(h)
            return True
        except Exception:
            return False
    finally:
        win32service.CloseServiceHandle(scm)


def service_status() -> str:
    if not _HAS_WIN32 or not service_exists():
        return 'missing'
    scm = _open_scm(win32service.SC_MANAGER_CONNECT)
    try:
        h = win32service.OpenService(scm, SERVICE_NAME, win32service.SERVICE_QUERY_STATUS)
        try:
            state = win32service.QueryServiceStatus(h)[1]
        finally:
            win32service.CloseServiceHandle(h)
    finally:
        win32service.CloseServiceHandle(scm)
    return {
        win32service.SERVICE_RUNNING: 'running',
        win32service.SERVICE_STOPPED: 'stopped',
        win32service.SERVICE_START_PENDING: 'start_pending',
        win32service.SERVICE_STOP_PENDING: 'stop_pending',
    }.get(state, 'unknown')


def install_service() -> None:
    """Create (or update) the Windows service and set auto-start."""
    if not _HAS_WIN32:
        raise RuntimeError('pywin32 no disponible en este sistema.')
    exe = _exe_path()
    bin_path = f'"{exe}" --service' if not exe.startswith('"') else f'{exe} --service'
    scm = _open_scm(win32service.SC_MANAGER_ALL_ACCESS)
    try:
        if service_exists():
            h = win32service.OpenService(scm, SERVICE_NAME, win32service.SERVICE_ALL_ACCESS)
            try:
                win32service.ChangeServiceConfig(
                    h,
                    win32service.SERVICE_WIN32_OWN_PROCESS,
                    win32service.SERVICE_AUTO_START,
                    win32service.SERVICE_ERROR_NORMAL,
                    bin_path,
                    None, 0, None, None, None,
                    SERVICE_DISPLAY,
                )
                try:
                    win32service.ChangeServiceConfig2(
                        h, win32service.SERVICE_CONFIG_DESCRIPTION, SERVICE_DESCRIPTION
                    )
                except Exception:
                    pass
            finally:
                win32service.CloseServiceHandle(h)
        else:
            h = win32service.CreateService(
                scm,
                SERVICE_NAME,
                SERVICE_DISPLAY,
                win32service.SERVICE_ALL_ACCESS,
                win32service.SERVICE_WIN32_OWN_PROCESS,
                win32service.SERVICE_AUTO_START,
                win32service.SERVICE_ERROR_NORMAL,
                bin_path,
                None, 0, None, None, None,
            )
            try:
                try:
                    win32service.ChangeServiceConfig2(
                        h, win32service.SERVICE_CONFIG_DESCRIPTION, SERVICE_DESCRIPTION
                    )
                except Exception:
                    pass
            finally:
                win32service.CloseServiceHandle(h)
    finally:
        win32service.CloseServiceHandle(scm)


def uninstall_service() -> None:
    if not _HAS_WIN32 or not service_exists():
        return
    try:
        stop_service(timeout=15)
    except Exception:
        pass
    scm = _open_scm(win32service.SC_MANAGER_ALL_ACCESS)
    try:
        h = win32service.OpenService(scm, SERVICE_NAME, win32service.SERVICE_ALL_ACCESS)
        try:
            win32service.DeleteService(h)
        finally:
            win32service.CloseServiceHandle(h)
    finally:
        win32service.CloseServiceHandle(scm)


def start_service(timeout: int = 20) -> None:
    if not _HAS_WIN32:
        raise RuntimeError('pywin32 no disponible.')
    if not service_exists():
        raise RuntimeError('El servicio no está instalado.')
    if service_status() == 'running':
        return
    win32serviceutil.StartService(SERVICE_NAME)
    deadline = time.time() + timeout
    while time.time() < deadline:
        if service_status() == 'running':
            return
        time.sleep(0.5)
    raise RuntimeError('El servicio no llegó a estado "running" a tiempo.')


def stop_service(timeout: int = 20) -> None:
    if not _HAS_WIN32 or not service_exists():
        return
    if service_status() == 'stopped':
        return
    try:
        win32serviceutil.StopService(SERVICE_NAME)
    except Exception:
        return
    deadline = time.time() + timeout
    while time.time() < deadline:
        if service_status() == 'stopped':
            return
        time.sleep(0.5)


def restart_service(timeout: int = 30) -> None:
    stop_service(timeout=timeout)
    start_service(timeout=timeout)


if _HAS_WIN32:

    class ReviewBoostService(win32serviceutil.ServiceFramework):  # type: ignore[misc]
        _svc_name_ = SERVICE_NAME
        _svc_display_name_ = SERVICE_DISPLAY
        _svc_description_ = SERVICE_DESCRIPTION

        def __init__(self, args):
            super().__init__(args)
            self._stop_event = win32event.CreateEvent(None, 0, 0, None)
            self._stop_flag = threading.Event()

        def SvcStop(self):
            self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
            self._stop_flag.set()
            win32event.SetEvent(self._stop_event)

        def SvcDoRun(self):
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STARTED,
                (self._svc_name_, ''),
            )
            from reviewboost_agent.scheduler import run_forever
            run_forever(stop_flag=self._stop_flag)

else:
    ReviewBoostService = None  # type: ignore


def run_service_dispatch() -> None:
    """Entry point used when SCM launches the frozen exe with ``--service``."""
    if not _HAS_WIN32:
        raise RuntimeError('pywin32 no disponible; no puede ejecutarse como servicio.')
    servicemanager.Initialize()
    servicemanager.PrepareToHostSingle(ReviewBoostService)
    servicemanager.StartServiceCtrlDispatcher()
