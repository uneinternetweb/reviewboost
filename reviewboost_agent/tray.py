"""System tray icon."""
from __future__ import annotations
import threading
from pathlib import Path
from PIL import Image
import pystray

from .scheduler import run_once
from .setup_wizard import open_wizard

def _icon() -> Image.Image:
    ico = Path(__file__).with_name('icon.ico')
    if ico.exists():
        return Image.open(ico)
    return Image.new('RGB', (64, 64), color=(42, 157, 143))

def _sync(icon, item):
    threading.Thread(target=lambda: run_once(force=True), daemon=True).start()

def _configure(icon, item):
    threading.Thread(target=open_wizard, daemon=True).start()

def _quit(icon, item):
    icon.stop()

def run_tray() -> None:
    menu = pystray.Menu(
        pystray.MenuItem('Sincronizar ahora', _sync),
        pystray.MenuItem('Configurar…', _configure),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem('Salir', _quit),
    )
    pystray.Icon('ReviewBoostAgent', _icon(), 'Review Boost Agent', menu).run()