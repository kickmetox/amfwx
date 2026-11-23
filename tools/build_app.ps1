param([string]$Name = "AMFWX")
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
if (-not (Get-Command pyinstaller -ErrorAction SilentlyContinue)) {
    throw "PyInstaller fehlt: python -m pip install pyinstaller"
}
$icon = Join-Path $Root "assets\AMFWX.ico"
if (Test-Path $icon) {
    python -m PyInstaller --noconfirm --clean --windowed --name $Name --icon $icon tools\amfwx_app.py
} else {
    python -m PyInstaller --noconfirm --clean --windowed --name $Name tools\amfwx_app.py
}
if ($LASTEXITCODE -ne 0) { throw "PyInstaller fehlgeschlagen" }
Write-Host "dist\$Name\$Name.exe"
