"""Tkinter wizard to configure the agent."""
from __future__ import annotations
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from .config import load_config, save_config
from .mdb_reader import test_connection
from .sync_client import SyncClient
try:
    from .service import install_service, start_service, restart_service
except Exception:  # pragma: no cover
    install_service = start_service = restart_service = None


def open_wizard() -> None:
    cfg = load_config()
    root = tk.Tk()
    root.title('Review Boost — Configuración del agente')
    root.geometry('620x420'); root.resizable(False, False)
    frm = ttk.Frame(root, padding=16); frm.pack(fill='both', expand=True)

    ttk.Label(frm, text='Ruta al archivo .mdb de Drtooth').grid(row=0, column=0, columnspan=3, sticky='w')
    path_var = tk.StringVar(value=cfg.mdb_path)
    ttk.Entry(frm, textvariable=path_var, width=64).grid(row=1, column=0, columnspan=2, sticky='we', pady=(2, 8))
    def browse():
        p = filedialog.askopenfilename(filetypes=[('Access DB', '*.mdb *.accdb'), ('Todos', '*.*')])
        if p: path_var.set(p)
    ttk.Button(frm, text='Examinar…', command=browse).grid(row=1, column=2, padx=(8, 0), pady=(2, 8))

    ttk.Label(frm, text='Contraseña del MDB').grid(row=2, column=0, columnspan=3, sticky='w')
    pwd_var = tk.StringVar(value=cfg.mdb_password)
    pwd_entry = ttk.Entry(frm, textvariable=pwd_var, show='•', width=64)
    pwd_entry.grid(row=3, column=0, columnspan=2, sticky='we', pady=(2, 8))
    show_var = tk.BooleanVar(value=False)
    def toggle_show():
        pwd_entry.config(show='' if show_var.get() else '•')
    ttk.Checkbutton(frm, text='Mostrar', variable=show_var, command=toggle_show).grid(row=3, column=2, padx=(8, 0))

    ttk.Label(frm, text='Clave del agente (copiada desde el panel Review Boost)').grid(row=4, column=0, columnspan=3, sticky='w')
    key_var = tk.StringVar(value=cfg.agent_api_key)
    ttk.Entry(frm, textvariable=key_var, show='•', width=64).grid(row=5, column=0, columnspan=3, sticky='we', pady=(2, 12))

    status_var = tk.StringVar(value='')
    ttk.Label(frm, textvariable=status_var, foreground='#555', wraplength=560, justify='left').grid(row=6, column=0, columnspan=3, sticky='w')

    def save_and_test():
        cfg.mdb_path = path_var.get().strip()
        cfg.mdb_password = pwd_var.get()
        cfg.agent_api_key = key_var.get().strip()
        if not cfg.is_ready():
            messagebox.showerror('Faltan datos', 'La ruta del MDB y la clave del agente son obligatorias.')
            return

        status_var.set('Descargando mapeo desde Review Boost…'); root.update_idletasks()
        try:
            remote = SyncClient(cfg.api_base, cfg.agent_api_key).get_config()
        except Exception as exc:
            messagebox.showerror(
                'Error al descargar mapeo',
                'No se pudo obtener la configuración desde Review Boost.\n'
                'Comprueba la clave del agente, internet y el mapeo MDB en la app.\n\n'
                f'{exc}',
            )
            status_var.set(''); return

        status_var.set(f'Probando MDB con tabla "{remote.table_name}"…'); root.update_idletasks()
        try:
            count = test_connection(cfg.mdb_path, cfg.mdb_password, remote.table_name)
        except Exception as exc:
            messagebox.showerror(
                'Error de conexión',
                f'No se pudo abrir la tabla "{remote.table_name}" del MDB.\n'
                'Verifica que el nombre de tabla configurado en Review Boost coincide exactamente con el MDB.\n\n'
                f'{exc}',
            )
            status_var.set(''); return

        save_config(cfg)
        service_msg = ''
        if install_service and start_service:
            status_var.set('MDB OK. Instalando servicio Windows…'); root.update_idletasks()
            try:
                install_service()
                try:
                    start_service()
                except Exception:
                    if restart_service:
                        restart_service()
                service_msg = '\nServicio Windows instalado/iniciado.'
            except Exception as exc:
                service_msg = f'\nATENCIÓN: no se pudo instalar/iniciar el servicio: {exc}\nEjecuta el asistente como administrador.'

        messagebox.showinfo(
            'Guardado',
            f'Conexión correcta. Tabla "{remote.table_name}" con {count} registros.\n'
            f'Configuración guardada cifrada en este PC.{service_msg}'
        )
        root.destroy()

    btns = ttk.Frame(frm); btns.grid(row=7, column=0, columnspan=3, sticky='e', pady=(16, 0))
    ttk.Button(btns, text='Cancelar', command=root.destroy).pack(side='right', padx=(8, 0))
    ttk.Button(btns, text='Guardar, probar e instalar servicio', command=save_and_test).pack(side='right')
    frm.columnconfigure(0, weight=1)
    root.mainloop()

if __name__ == '__main__':
    open_wizard()
