; Inno Setup script for Review Boost Windows agent
#define AppName "Review Boost Agent"
#define AppVersion "1.0.0"
#define AppExeName "reviewboost-agent.exe"

[Setup]
AppId={{6C5B2C4E-9A2E-4C11-9E9A-8BF6E9E9E9E9}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher=Review Boost
DefaultDirName={autopf}\ReviewBoost\Agent
DefaultGroupName=Review Boost
DisableProgramGroupPage=yes
PrivilegesRequired=admin
OutputBaseFilename=ReviewBoostAgentSetup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64

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
var Version: String;
begin
  Result := True;
  if not RegQueryStringValue(HKLM64, 'SOFTWARE\Microsoft\Office\16.0\Access Connectivity Engine\InstallRoot', 'Path', Version) then
  begin
    if MsgBox('No se ha detectado Microsoft Access Database Engine 2016 (x64).'#13#10 +
             'Descárgalo en https://www.microsoft.com/download/details.aspx?id=54920'#13#10 +
             '¿Continuar de todos modos?', mbConfirmation, MB_YESNO) = IDNO then
      Result := False;
  end;
end;