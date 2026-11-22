param(
    [string]$Exe = ""
)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
if (-not $Exe) {
    $Exe = Join-Path $Root "dist\AMFWX\AMFWX.exe"
}
if (-not (Test-Path $Exe)) { throw "EXE fehlt: $Exe" }
$cert = New-SelfSignedCertificate `
    -Type CodeSigningCert `
    -Subject "CN=AMFWX Test Signing" `
    -CertStoreLocation "Cert:\CurrentUser\My" `
    -KeyExportPolicy Exportable `
    -KeyUsage DigitalSignature `
    -TextExtension @("2.5.29.37={text}1.3.6.1.5.5.7.3.3")
Write-Host "Thumbprint: $($cert.Thumbprint)"
$signature = Set-AuthenticodeSignature -FilePath $Exe -Certificate $cert `
    -HashAlgorithm SHA256
Write-Host "Status: $($signature.Status)"
Write-Host "Hinweis: selbstsigniert -> Status UnknownError, bis das Zertifikat"
Write-Host "in Trusted Root/Trusted Publisher importiert ist."
Get-AuthenticodeSignature $Exe | Format-List Status, StatusMessage, SignerCertificate
