# Build script for Review Boost Windows agent.
$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue
    pyinstaller pyinstaller.spec --clean --noconfirm
    $iscc = "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe"
    if (-not (Test-Path $iscc)) { throw "Inno Setup not found at $iscc" }
    & $iscc installer/reviewboost-agent.iss
    Write-Host 'Installer at installer/Output/ReviewBoostAgentSetup.exe'
} finally {
    Pop-Location
}