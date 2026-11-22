param([string]$Target = "$env:LOCALAPPDATA\AMFWX")
$ErrorActionPreference = "Stop"
$programs = [Environment]::GetFolderPath("Programs")
$shortcut = Join-Path $programs "AMFWX.lnk"
if (Test-Path $shortcut) { Remove-Item $shortcut -Force }
if (Test-Path $Target) { Remove-Item $Target -Recurse -Force }
Write-Host "Deinstalliert: $Target"
