# Offene Punkte und Blocker

## 1. UIA-Hosting

Status: **Basis funktioniert** (native 1×1-Proxies)

Befund:

- `IUIAutomation::ElementFromHandle` funktioniert.
- Der Client sieht `Window` + native `TitleBar`.
- Es wird **kein `WM_GETOBJECT`** an das Python-Fenster gesendet.
- Der Custom-Provider wird deshalb nicht aufgerufen.
- `QI`, Simple-Vtable und GUID sind korrigiert.

Nächster technischer Ansatz:

- native Child-HWNDs pro Widget wurden getestet: UIA sieht sie nicht.
- 1×1- und 8×8-Varianten ohne Wirkung.
- `WS_EX_CONTROLPARENT` auf dem Hauptfenster getestet: ohne Wirkung.
- Der Client listet jetzt Text/Button/Edit-Proxies.
- Vollständige Screenreader-Zertifizierung bleibt offen.

## 2. WebP

Status: **nicht implementiert**

Es gibt keinen eigenen VP8/VP8L-Decoder. Ein vollständiger WebP-Codec
ist ein separates Projekt und nicht in einem Schritt seriös lieferbar.

## 3. SDL3

Status: **blockiert**

`SDL3.dll` ist auf dem System nicht vorhanden:

```text
missing SDL3.dll
missing C:\Windows\System32\SDL3.dll
```

Der SDL3-Probe erkennt das korrekt. Ohne DLL gibt es keinen testbaren
SDL3-Renderer.

## 4. Inno/signtool

Status: **blockiert**

```text
iscc:     vorhanden (vendor\inno\ISCC.exe)
signtool: vorhanden (SDK BuildTools NuGet)
CA-Zertifikat: lokal vertrauenswürdige Test-CA
Signaturstatus: Valid
```

PyInstaller ist vorhanden; die EXE wurde gebaut.
Der eigene Installer wurde mit `signtool.exe` und einer Test-CA signiert.
Status ist auf diesem System `Valid`.

## 5. COM-Thread-Isolation

Status: **weitgehend**

- `RLock` in Provider/TextProvider/TextRange.
- `Window.invoke` marshallt per `WM_APP_INVOKE` auf den UI-Thread.
- UIA-Callbacks werden serialisiert.
- Keine vollständige Thread-Affinitätsprüfung.

## 6. Screenreader-Test

Status: **nicht bestanden**

Voraussetzung ist ein funktionierendes UIA-Hosting. Solange der Client
kein `WM_GETOBJECT` sendet, kann kein Screenreader die Custom-Kinder sehen.

## Fazit

Drei Punkte sind **Umgebungsblocker**:

- WebP
- SDL3
- Inno/signtool

Zwei Punkte sind **technisch offen**:

- UIA-Hosting
- Screenreader-Test

Ein Punkt ist **teilweise umgesetzt**:

- COM-Thread-Isolation
