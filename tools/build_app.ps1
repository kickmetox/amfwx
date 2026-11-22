param([string]$Name = "AMFWX")
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
if (-not (Get-Command pyinstaller -ErrorAction SilentlyContinue)) {
    throw "PyInstaller fehlt: python -m pip install pyinstaller"
}
python -m PyInstaller --noconfirm --clean --windowed --name $Name tools\amfwx_app.py
if ($LASTEXITCODE -ne 0) { throw "PyInstaller fehlgeschlagen" }
Write-Host "dist\$Name\$Name.exe"
