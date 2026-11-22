# Eigener AMFWX-Installer

Kein Inno Setup. Der Installer ist eine eigene PyInstaller-Anwendung mit
AMFWX-GUI, Payload-ZIP, StartmenÃ¼-/Desktop-VerknÃ¼pfungen und Uninstaller.

## Bauen

```powershell
tools\build_app.ps1
python tools\build_own_installer.py
```

Ergebnis:

```text
dist\AMFWX-Own-Setup-1.1.2.exe
```

## Installieren

GUI:

```bat
dist\AMFWX-Own-Setup-1.1.2.exe
```

Silent:

```bat
dist\AMFWX-Own-Setup-1.1.2.exe /S /D=D:\Apps\AMFWX
```

Ohne `/D=`:

```text
%LOCALAPPDATA%\Programs\AMFWX
```

## Was der Installer macht

- entpackt `payload.zip`
- kopiert `AMFWX.exe` und `_internal`
- erstellt Desktop- und StartmenÃ¼-VerknÃ¼pfung
- schreibt `uninstall.cmd`
- registriert sich unter:

```text
HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\AMFWX
```

## Deinstallieren

```bat
uninstall.cmd
```

Entfernt:

- Installationsordner
- Registry-Eintrag
- Desktop-VerknÃ¼pfung
- StartmenÃ¼-VerknÃ¼pfung

## Getestet

Silent-Installation nach `D:\AI_Temp\AMFWX\test_install`:

```text
exit=0
AMFWX.exe
_internal
uninstall.cmd
```

Registry:

```text
DisplayName     AMFWX
DisplayVersion  1.1.2
InstallLocation D:\AI_Temp\AMFWX\test_install
```

Desktop-VerknÃ¼pfung wurde erstellt.
Deinstallation entfernte Ordner und Registry-Eintrag.

## Signatur

Mit `tools/sign_selfsigned.ps1` signiert:

```text
Status: Valid
```

Grund: lokale Test-CA im Trusted-Root-/TrustedPublisher-Store.

SHA-256:

```text
6810AFDEDD49ECB4332C9644B94D2F65E934E8E5DD24DA0FFED3892ADA495D43
```

## Grenzen

- kein MSI
- keine automatische Update-PrÃ¼fung
- keine CA-signierte Reputation
- GUI-Extraktion lÃ¤uft im UI-Thread
- Uninstaller ist ein CMD-Skript

