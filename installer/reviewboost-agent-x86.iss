; Inno Setup script for Review Boost Windows agent x86
#define AppName "Review Boost Agent"
#define AppVersion "1.0.2-x86"
#define AppExeName "reviewboost-agent.exe"

[Setup]
AppId={{6C5B2C4E-9A2E-4C11-9E9A-8BF6E9E9E9E9}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher=Review Boost
DefaultDirName={autopf32}\ReviewBoost\Agent
DefaultGroupName=Review Boost
DisableProgramGroupPage=yes
PrivilegesRequired=admin
OutputBaseFilename=ReviewBoostAgentSetup-x86
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x86 x64

[Files]
Source: "..\dist\reviewboost-agent.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Configurar Review Boost Agent"; Filename: "{app}\{#AppExeName}"
Name: "{group}\Uninstall"; Filename: "{uninstallexe}"

[Run]
; El propio agente registra el servicio nativo de Windows mediante pywin32.
; NSSM no es necesario.
Filename: "{app}\{#AppExeName}"; Parameters: "--install-service"; Flags: runhidden waituntilterminated
Filename: "{app}\{#AppExeName}"; Description: "Configurar el agente ahora"; Flags: nowait postinstall skipifsilent

[UninstallRun]
Filename: "{app}\{#AppExeName}"; Parameters: "--uninstall-service"; Flags: runhidden waituntilterminated

[Code]
function InitializeSetup(): Boolean;
begin
  Result := True;
  MsgBox('Esta versión del agente es de 32 bits y está pensada para equipos con Office/Access de 32 bits.'#13#10 +
         'Si el controlador Microsoft Access Driver (*.mdb, *.accdb) ya aparece en ODBC (32 bits), no necesitas instalar Access Database Engine x64.',
         mbInformation, MB_OK);
end;
