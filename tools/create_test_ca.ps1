param(
    [string]$Installer = "",
    [string]$Signtool = "$env:TEMP\sdkbuildtools\bin\10.0.26100.0\x64\signtool.exe"
)
$ErrorActionPreference = "Stop"
if (-not $Installer) {
    $Installer = Get-ChildItem "dist\AMFWX-Own-Setup-*.exe" |
        Sort-Object LastWriteTime -Descending | Select-Object -First 1 -ExpandProperty FullName
}
if (-not (Test-Path $Installer)) { throw "Installer fehlt" }
if (-not (Test-Path $Signtool)) { throw "signtool fehlt: $Signtool" }

$root = New-SelfSignedCertificate `
    -Type Custom -Subject "CN=AMFWX Test Root" `
    -KeyUsage CertSign,CRLSign,DigitalSignature `
    -KeyExportPolicy Exportable -CertStoreLocation "Cert:\CurrentUser\My" `
    -TextExtension @("2.5.29.19={text}CA=true&pathlength=1") `
    -NotAfter (Get-Date).AddYears(5)
$code = New-SelfSignedCertificate `
    -Type CodeSigningCert -Subject "CN=AMFWX Code Signing" `
    -Signer $root -CertStoreLocation "Cert:\CurrentUser\My" `
    -KeyExportPolicy Exportable -NotAfter (Get-Date).AddYears(2)

$rootCer = Join-Path $env:TEMP "amfwx_root.cer"
Export-Certificate -Cert $root -FilePath $rootCer | Out-Null
certutil -addstore -user -f Root $rootCer | Out-Null
certutil -addstore -user -f TrustedPublisher $rootCer | Out-Null

$pfx = Join-Path $env:TEMP "amfwx_ca.pfx"
$password = ConvertTo-SecureString "amfwx-ca" -Force -AsPlainText
Export-PfxCertificate -Cert $code -FilePath $pfx -Password $password | Out-Null

& $Signtool sign /fd SHA256 /f $pfx /p "amfwx-ca" /sha1 $code.Thumbprint `
    /t http://timestamp.digicert.com $Installer
Get-AuthenticodeSignature $Installer | Format-List Status, SignerCertificate
