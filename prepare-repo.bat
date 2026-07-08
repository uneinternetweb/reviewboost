@echo off
REM Prepara una carpeta lista para subir a GitHub como repositorio del agente.
REM Uso: prepare-repo.bat C:\ruta\destino\reviewboost-agent

if "%~1"=="" (
  echo Uso: %~nx0 C:\ruta\destino\reviewboost-agent
  echo.
  echo Crea una copia limpia de los archivos del agente para subir a GitHub.
  exit /b 1
)

set "DEST_DIR=%~1"
set "SCRIPT_DIR=%~dp0"

if not exist "%DEST_DIR%" mkdir "%DEST_DIR%"

xcopy /E /I /Y "%SCRIPT_DIR%.github" "%DEST_DIR%\.github" >nul
xcopy /E /I /Y "%SCRIPT_DIR%reviewboost_agent" "%DEST_DIR%\reviewboost_agent" >nul
xcopy /E /I /Y "%SCRIPT_DIR%installer" "%DEST_DIR%\installer" >nul
copy /Y "%SCRIPT_DIR%build.ps1" "%DEST_DIR%\" >nul
copy /Y "%SCRIPT_DIR%pyinstaller.spec" "%DEST_DIR%\" >nul
copy /Y "%SCRIPT_DIR%requirements.txt" "%DEST_DIR%\" >nul
copy /Y "%SCRIPT_DIR%README.md" "%DEST_DIR%\" >nul
copy /Y "%SCRIPT_DIR%.gitignore" "%DEST_DIR%\" >nul

echo Agente copiado a: %DEST_DIR%
echo.
echo Pasos siguientes:
echo   cd %DEST_DIR%
echo   git init
echo   git add .
echo   git commit -m "Initial agent release"
echo   git branch -M main
echo   git remote add origin https://github.com/TU_USUARIO/reviewboost-agent.git
echo   git push -u origin main
echo   git tag v1.0.0
echo   git push origin v1.0.0
echo.
echo Despues de 5-10 minutos, la URL de descarga sera:
echo   https://github.com/TU_USUARIO/reviewboost-agent/releases/latest/download/ReviewBoostAgentSetup.exe
