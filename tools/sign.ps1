param(
    [string]$File = "",
    [string]$Certificate = $env:AMFWX_CERT,
    [string]$TimestampUrl = "http://timestamp.digicert.com"
)
$ErrorActionPreference = "Stop"
if (-not $File) {
    $File = Get-ChildItem "dist\installer\*.exe" -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending | Select-Object -First 1 -ExpandProperty FullName
}
if (-not $File -or -not (Test-Path $File)) { throw "Kein Installer gefunden" }
if (-not $Certificate) { throw "AMFWX_CERT fehlt" }
$signtool = Get-Command signtool.exe -ErrorAction SilentlyContinue
if (-not $signtool) { throw "signtool.exe fehlt" }
& $signtool sign /fd SHA256 /tr $TimestampUrl /td SHA256 /f $Certificate $File
if ($LASTEXITCODE -ne 0) { throw "Signierung fehlgeschlagen" }
