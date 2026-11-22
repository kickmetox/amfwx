param([string]$File = "")
$ErrorActionPreference = "Stop"
if (-not $File) {
    $File = Get-ChildItem "dist\installer\*.exe" -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending | Select-Object -First 1 -ExpandProperty FullName
}
if (-not $File) { throw "Kein Installer gefunden" }
$hash = Get-FileHash -Algorithm SHA256 $File
$signature = Get-AuthenticodeSignature $File
Write-Host "SHA-256: $($hash.Hash)"
Write-Host "Status:  $($signature.Status)"
if ($signature.Status -ne "Valid") { throw "Authenticode ungültig: $($signature.Status)" }
