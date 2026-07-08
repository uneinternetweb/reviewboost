"""Tkinter wizard to configure the agent."""
from __future__ import annotations
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from .config import load_config, save_config
from .mdb_reader import test_connection

def open_wizard() -> None:
    cfg = load_config()
    root = tk.Tk()
    root.title('Review Boost — Configuración del agente')
    root.geometry('540x360'); root.resizable(False, False)
    frm = ttk.Frame(root, padding=16); frm.pack(fill='both', expand=True)

    ttk.Label(frm, text='Ruta al archivo .mdb de Drtooth').grid(row=0, column=0, columnspan=3, sticky='w')
    path_var = tk.StringVar(value=cfg.mdb_path)
    ttk.Entry(frm, textvariable=path_var, width=54).grid(row=1, column=0, columnspan=2, sticky='we', pady=(2, 8))
    def browse():
        p = filedialog.askopenfilename(filetypes=[('Access DB', '*.mdb *.accdb'), ('Todos', '*.*')])
        if p: path_var.set(p)
    ttk.Button(frm, text='Examinar…', command=browse).grid(row=1, column=2, padx=(8, 0), pady=(2, 8))

    ttk.Label(frm, text='Contraseña del MDB').grid(row=2, column=0, columnspan=3, sticky='w')
    pwd_var = tk.StringVar(value=cfg.mdb_password)
    pwd_entry = ttk.Entry(frm, textvariable=pwd_var, show='•', width=54)
    pwd_entry.grid(row=3, column=0, columnspan=2, sticky='we', pady=(2, 8))
    show_var = tk.BooleanVar(value=False)
    def toggle_show():
        pwd_entry.config(show='' if show_var.get() else '•')
    ttk.Checkbutton(frm, text='Mostrar', variable=show_var, command=toggle_show).grid(row=3, column=2, padx=(8, 0))

    ttk.Label(frm, text='Clave del agente (copiada desde el panel Review Boost)').grid(row=4, column=0, columnspan=3, sticky='w')
    key_var = tk.StringVar(value=cfg.agent_api_key)
    ttk.Entry(frm, textvariable=key_var, show='•', width=54).grid(row=5, column=0, columnspan=3, sticky='we', pady=(2, 12))

    status_var = tk.StringVar(value='')
    ttk.Label(frm, textvariable=status_var, foreground='#555').grid(row=6, column=0, columnspan=3, sticky='w')

    def save_and_test():
        cfg.mdb_path = path_var.get().strip()
        cfg.mdb_password = pwd_var.get()
        cfg.agent_api_key = key_var.get().strip()
        if not cfg.is_ready():
            messagebox.showerror('Faltan datos', 'La ruta del MDB y la clave del agente son obligatorias.')
            return
        status_var.set('Probando conexión con el MDB…'); root.update_idletasks()
        try:
            count = test_connection(cfg.mdb_path, cfg.mdb_password)
        except Exception as exc:
            messagebox.showerror('Error de conexión', f'No se pudo abrir el MDB:\n{exc}')
            status_var.set(''); return
        save_config(cfg)
        messagebox.showinfo('Guardado', f'Conexión correcta. {count} registros detectados.\nConfiguración guardada cifrada en este PC.')
        root.destroy()

    btns = ttk.Frame(frm); btns.grid(row=7, column=0, columnspan=3, sticky='e', pady=(16, 0))
    ttk.Button(btns, text='Cancelar', command=root.destroy).pack(side='right', padx=(8, 0))
    ttk.Button(btns, text='Guardar y probar', command=save_and_test).pack(side='right')
    frm.columnconfigure(0, weight=1)
    root.mainloop()

if __name__ == '__main__':
    open_wizard()