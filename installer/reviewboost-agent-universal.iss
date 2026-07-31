; Universal Inno Setup script for Review Boost Windows agent
#define AppName "Review Boost Agent"
#define AppVersion "1.1.0"
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
ArchitecturesAllowed=x86 x64

[Files]
Source: "..\package\x86\reviewboost-agent.exe"; DestDir: "{app}"; DestName: "{#AppExeName}"; Flags: ignoreversion; Check: UseX86
Source: "..\package\x64\reviewboost-agent.exe"; DestDir: "{app}"; DestName: "{#AppExeName}"; Flags: ignoreversion; Check: UseX64

[Icons]
Name: "{group}\Configurar Review Boost Agent"; Filename: "{app}\{#AppExeName}"
Name: "{group}\Uninstall"; Filename: "{uninstallexe}"

[Run]
Filename: "{app}\{#AppExeName}"; Parameters: "--install-service"; Flags: runhidden waituntilterminated
Filename: "{app}\{#AppExeName}"; Description: "Configurar el agente ahora"; Flags: nowait postinstall skipifsilent

[UninstallRun]
Filename: "{app}\{#AppExeName}"; Parameters: "--uninstall-service"; Flags: runhidden waituntilterminated

[Code]
var
  SelectedArch: String;

function HasAccessDriver32(): Boolean;
var
  Dummy: String;
begin
  Result := RegQueryStringValue(HKLM32,
    'SOFTWARE\ODBC\ODBCINST.INI\Microsoft Access Driver (*.mdb, *.accdb)',
    'Driver', Dummy);
end;

function HasAccessDriver64(): Boolean;
var
  Dummy: String;
begin
  if not IsWin64 then
  begin
    Result := False;
    exit;
  end;
  Result := RegQueryStringValue(HKLM64,
    'SOFTWARE\ODBC\ODBCINST.INI\Microsoft Access Driver (*.mdb, *.accdb)',
    'Driver', Dummy);
end;

function UseX86(): Boolean;
begin
  Result := SelectedArch = 'x86';
end;

function UseX64(): Boolean;
begin
  Result := SelectedArch = 'x64';
end;

function InitializeSetup(): Boolean;
var
  Has32, Has64: Boolean;
begin
  Result := True;
  Has32 := HasAccessDriver32();
  Has64 := HasAccessDriver64();

  if Has32 then
    SelectedArch := 'x86'
  else if Has64 then
    SelectedArch := 'x64'
  else
  begin
    if IsWin64 then
      SelectedArch := 'x64'
    else
      SelectedArch := 'x86';

    MsgBox(
      'No se ha detectado el controlador Microsoft Access Driver (*.mdb, *.accdb) en este equipo.'#13#10#13#10 +
      'El agente se instalará igualmente, pero la conexión al MDB no funcionará hasta que exista un controlador Access ODBC compatible.'#13#10#13#10 +
      'Arquitectura seleccionada: ' + SelectedArch + '.',
      mbInformation, MB_OK);
  end;
end;

procedure CurPageChanged(CurPageID: Integer);
begin
  if CurPageID = wpReady then
    WizardForm.ReadyMemo.Lines.Add('Arquitectura del agente seleccionada: ' + SelectedArch);
end;
