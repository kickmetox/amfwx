param([string]$Name = "AMFWX")
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
if (-not (Get-Command pyinstaller -ErrorAction SilentlyContinue)) {
    throw "PyInstaller fehlt: python -m pip install pyinstaller"
}
$icon = Join-Path $Root "assets\AMFWX.ico"
$manifest = Join-Path $Root "assets\AMFWX.manifest"
$version = Join-Path $Root "assets\version_info.txt"
$extra = @()
if (Test-Path $icon) { $extra += @("--icon", $icon) }
if (Test-Path $manifest) { $extra += @("--manifest", $manifest) }
if (Test-Path $version) { $extra += @("--version-file", $version) }
python -m PyInstaller --noconfirm --clean --windowed --name $Name @extra tools\amfwx_app.py
if ($LASTEXITCODE -ne 0) { throw "PyInstaller fehlgeschlagen" }
Write-Host "dist\$Name\$Name.exe"
