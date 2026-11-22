# AMFWX Installer und Authenticode

## Portable

```bat
python tools\build_portable.py
```

Ergebnis:

```text
dist\AMFWX-Portable-<version>.zip
```

Getestet: `install.ps1` und `uninstall.ps1`.

## PyInstaller

```bat
tools\build_app.ps1
```

Ergebnis:

```text
dist\AMFWX\AMFWX.exe
```

## Inno Setup

```bat
tools\build_installer.ps1
```

Ergebnis:

```text
dist\installer\AMFWX-Setup-<version>.exe
```

Voraussetzungen:

- PyInstaller
- Inno Setup 6

## Authenticode

```bat
set AMFWX_CERT=C:\certs\codesign.pfx
set AMFWX_CERT_PASSWORD=...
tools\sign.ps1 -File dist\installer\AMFWX-Setup-0.12.0.exe
tools\verify_installer.ps1
```

Nicht ausgeführt:

- kein Zertifikat
- kein signtool in dieser Umgebung
- kein signierter Installer

## Grenzen

- keine eingebettete Python-Runtime
- kein MSIX
- keine Update-Signatur
- keine SmartScreen-Reputation
