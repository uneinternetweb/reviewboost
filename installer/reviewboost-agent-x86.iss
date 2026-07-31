; Inno Setup script for Review Boost Windows agent x86
#define AppName "Review Boost Agent"
#define AppVersion "1.0.1-x86"
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
Source: "nssm\nssm.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Configurar Review Boost Agent"; Filename: "{app}\{#AppExeName}"
Name: "{group}\Uninstall"; Filename: "{uninstallexe}"

[Run]
Filename: "{app}\nssm.exe"; Parameters: "install ReviewBoostAgent ""{app}\{#AppExeName}"" --service"; Flags: runhidden
Filename: "{app}\nssm.exe"; Parameters: "set ReviewBoostAgent Start SERVICE_AUTO_START"; Flags: runhidden
Filename: "{app}\nssm.exe"; Parameters: "set ReviewBoostAgent Description ""Sincroniza pacientes del MDB de Drtooth con Review Boost"""; Flags: runhidden
Filename: "{app}\nssm.exe"; Parameters: "start ReviewBoostAgent"; Flags: runhidden
Filename: "{app}\{#AppExeName}"; Description: "Configurar el agente ahora"; Flags: nowait postinstall skipifsilent

[UninstallRun]
Filename: "{app}\nssm.exe"; Parameters: "stop ReviewBoostAgent"; Flags: runhidden
Filename: "{app}\nssm.exe"; Parameters: "remove ReviewBoostAgent confirm"; Flags: runhidden

[Code]
function InitializeSetup(): Boolean;
begin
  Result := True;
  MsgBox('Esta versión del agente es de 32 bits y está pensada para equipos con Office/Access de 32 bits.'#13#10 +
         'Si el controlador Microsoft Access Driver (*.mdb, *.accdb) ya aparece en ODBC (32 bits), no necesitas instalar Access Database Engine x64.',
         mbInformation, MB_OK);
end;
