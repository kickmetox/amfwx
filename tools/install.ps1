param(
    [string]$Target = "$env:LOCALAPPDATA\AMFWX",
    [switch]$NoShortcut
)

$ErrorActionPreference = "Stop"
$Source = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not (Test-Path (Join-Path $Source "amfwx"))) {
    throw "amfwx-Paket fehlt"
}
if (Test-Path $Target) { Remove-Item $Target -Recurse -Force }
New-Item -ItemType Directory -Path $Target -Force | Out-Null
foreach ($item in @("amfwx", "examples", "README.md", "CHANGELOG.md", "AMFWX.cmd")) {
    $sourceItem = Join-Path $Source $item
    if (Test-Path $sourceItem) {
        Copy-Item $sourceItem (Join-Path $Target $item) -Recurse -Force
    }
}
if (-not $NoShortcut) {
    $shell = New-Object -ComObject WScript.Shell
    $programs = [Environment]::GetFolderPath("Programs")
    $shortcut = $shell.CreateShortcut((Join-Path $programs "AMFWX.lnk"))
    $shortcut.TargetPath = (Join-Path $Target "AMFWX.cmd")
    $shortcut.WorkingDirectory = $Target
    $shortcut.Save()
}
Write-Host "Installiert nach $Target"
