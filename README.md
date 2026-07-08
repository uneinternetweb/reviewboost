# Review Boost — Agente Windows para importación desde MDB (Drtooth)

Este agente lee el archivo `.mdb` de Drtooth en el PC de la clínica y envía los pacientes nuevos a Review Boost. La contraseña del MDB nunca sale del ordenador — se guarda cifrada con DPAPI de Windows.

## Instalación

1. Descarga `ReviewBoostAgentSetup.exe` desde la URL que aparece en el panel de Review Boost (campo *URL de descarga del instalador* en la sección de sincronización MDB). Esa URL apunta a la **última release de tu propio repositorio GitHub**, por ejemplo:
   `https://github.com/tu-usuario/tu-repo/releases/latest/download/ReviewBoostAgentSetup.exe`
   - Review Boost no aloja el instalador; cada cuenta/proyecto debe compilar y publicar el suyo propio siguiendo los pasos de [Compilación automática](#opci%C3%B3n-a--compilaci%C3%B3n-autom%C3%A1tica-con-github-actions-recomendada).
2. Ejecuta el instalador como administrador. Instalará:
   - El servicio de Windows `ReviewBoostAgent` (arranca automáticamente).
   - Un icono en la bandeja del sistema para configurar y forzar sincronizaciones.
3. Si falta el **Microsoft Access Database Engine 2016 (x64)**, el instalador te avisará con el enlace de descarga.
4. Se abrirá el asistente pidiendo:
   - **Ruta al archivo `.mdb`** (ej. `C:\Drtooth\datos\pacientes.mdb`).
   - **Contraseña del MDB** (oculta con puntitos).
   - **Clave del agente** (se genera desde el panel super admin de Review Boost).
5. Pulsa **Guardar y probar**. Si la conexión es correcta el servicio empezará a sincronizar.

## Configuración avanzada

El fichero cifrado vive en `%PROGRAMDATA%\ReviewBoost\config.dat`. Sólo la cuenta `LOCAL_MACHINE` de ese PC puede descifrarlo. Para migrar a otro PC hay que reinstalar y volver a introducir los datos.

Los logs se rotan en `%LOCALAPPDATA%\ReviewBoost\logs\agent.log`.

## Compilación (para desarrolladores)

### Opción A — Compilación automática con GitHub Actions (recomendada)

Este repositorio incluye un workflow en `.github/workflows/build.yml` que compila el instalador en un runner `windows-latest`:

1. Crea un repositorio **público** en GitHub (por ejemplo `reviewboost-agent`). Público es recomendado porque las releases privadas no permiten descarga directa sin autenticación.
2. Sube **solo el contenido de la carpeta `agent/`** a la raíz del nuevo repositorio. La estructura debe quedar:
   ```
   .github/workflows/build.yml
   reviewboost_agent/
   installer/
   build.ps1
   pyinstaller.spec
   requirements.txt
   README.md
   ```
   No subas todo el proyecto Review Boost; el workflow espera que los archivos del agente estén en la raíz.
3. Crea un tag con formato `v1.0.0` y haz push:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```
4. Eso disparará automáticamente el workflow `Build Windows agent` en la pestaña **Actions**. Espera unos 5-10 minutos.
5. El `.exe` se publicará automáticamente como asset en la pestaña **Releases** del repositorio. La URL directa y permanente a la última versión será:
   `https://github.com/<owner>/<repo>/releases/latest/download/ReviewBoostAgentSetup.exe`
   - Ejemplo: `https://github.com/miusuario/reviewboost-agent/releases/latest/download/ReviewBoostAgentSetup.exe`
6. En el panel de Review Boost, pega esa URL en el campo **URL de descarga del instalador** dentro de la sección *Sincronización desde MDB (Access)*. El botón de descarga se activará automáticamente para esa clínica.

También puedes lanzar la compilación a mano desde la pestaña Actions → **Build Windows agent** → *Run workflow*.

### Opción B — Compilación local

Requisitos: Windows 10/11, Python 3.11+, Inno Setup 6, NSSM 2.24.

```powershell
cd agent
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
.\build.ps1
```

El instalador final se genera en `agent/installer/Output/ReviewBoostAgentSetup.exe`.

## Modos de ejecución

| Comando | Descripción |
|---|---|
| `reviewboost-agent.exe` | Abre el asistente de configuración e icono de bandeja. |
| `reviewboost-agent.exe --service` | Modo servicio (lo llama NSSM automáticamente). |
| `reviewboost-agent.exe --run-once` | Ejecuta un ciclo de sincronización y sale (diagnóstico). |

## Seguridad

- La contraseña del MDB se cifra con `CryptProtectData` (scope `LOCAL_MACHINE`).
- La clave del agente se envía en el header `Authorization: Bearer …` sobre HTTPS.
- Sólo se leen las columnas configuradas (`ccod`, `cnome`, `cnome1`, `crtel1`, `crtel2`).
- Se usa un checkpoint incremental (`last_seen_max_code`) para leer únicamente pacientes nuevos, minimizando I/O y créditos.