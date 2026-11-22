# Authenticode – Testsignatur

## Build

```powershell
tools\build_app.ps1
```

Ergebnis:

```text
dist\AMFWX\AMFWX.exe
```

PyInstaller 6.11.1 war vorhanden; der Build wurde ausgeführt.

## Selbstsignierte Signatur

```powershell
tools\sign_selfsigned.ps1
```

Ergebnis:

- Zertifikat: `CN=AMFWX Test Signing`
- SHA-256-Signatur
- `SignerCertificate` vorhanden
- Status: `UnknownError`

Grund:

> Eine Zertifikatkette wurde zwar verarbeitet, endete jedoch mit einem
> Stammzertifikat, das beim Vertrauensanbieter nicht als vertrauenswürdig gilt.

Das ist bei einer selbstsignierten Testsignatur erwartbar.

## Echte Verteilung

Für `Status = Valid` ist nötig:

1. Code-Signing-Zertifikat einer vertrauenswürdigen CA
2. privater Schlüssel
3. `signtool.exe` aus dem Windows SDK
4. Zeitstempel-URL
5. optional SmartScreen-Reputation

```powershell
$env:AMFWX_CERT = "C:\certs\codesign.pfx"
tools\sign.ps1 -File dist\AMFWX\AMFWX.exe
tools\verify_installer.ps1
```

## Nicht ausgeführt

- Inno-Setup-Installer: `iscc` fehlt.
- signtool: fehlt.
- CA-Zertifikat: nicht vorhanden.
- SmartScreen-Reputation: nicht vorhanden.

## Artefakt

- `dist\AMFWX\AMFWX.exe`
- signiert mit selbstsigniertem Testzertifikat
- Hash: `D61FC43E4ABF62473DBD03D5AB8C6FD224C4E4EE3CA1048573BA4502AFCC4761`
