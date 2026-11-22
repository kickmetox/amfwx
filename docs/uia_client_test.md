# UIA-Client-Test

Getestet mit:

- Python-AMFWX-Fenster
- `UIAutomationClient`
- `AutomationElement.FromHandle`

## Ergebnis

Der Client sieht das Fenster:

```text
Name: AMFWX UIA Probe
ControlType: Window
```

Aber:

```text
Children: 0
```

Erwartet waren:

- Label
- Button
- TextEdit

## Diagnose

- `WM_GETOBJECT` wird empfangen.
- `UiaReturnRawElementProvider` wird aufgerufen.
- Der Client fällt trotzdem auf den nativen Fenster-Provider zurück.
- Ein geänderter Provider-Name (`CUSTOM_PROVIDER_NAME`) erscheint nicht.
- `FindAll(TreeScope.Children)` liefert 0.

## Behobene Punkte

- `GUID.__str__` ergänzt; QueryInterface verglich vorher Objekt-Repräsentationen
  und schlug für alle IIDs fehl.
- `IRawElementProviderSimple`-Vtable korrigiert: Host, Pattern, Property
  waren vertauscht.

- `WM_GETOBJECT`-Parameter werden jetzt durchgereicht.
- `NavigateDirection` korrigiert:
  - FirstChild = 1
  - LastChild = 2
  - NextSibling = 3
  - PreviousSibling = 4
- `IsControlElement`/`IsContentElement` liefern true.
- Host-RawElementProvider wieder aktiv.

## Offen

- Der Provider wird von UIA noch nicht als Fragment-Root akzeptiert, obwohl
  QueryInterface jetzt für Simple/Fragment/Root erfolgreich ist.
- Screenreader-/Inspect.exe-Test nicht bestanden.
- Kein `Status = Valid` für Accessibility.

## Regressionstests

- `GUID.__str__`
- QI für Simple/Fragment/Root
- Simple-Vtable: Host/Pattern/Property

## Konsequenz

Der Provider bleibt **opt-in** und intern testbar, aber nicht als
screenreader-produktionsreif dokumentiert.


## IUIAutomation-Client

Zusätzlicher Test mit `CoCreateInstance(CUIAutomation)`:

```text
CoCreateInstance 0x0
GetRootElement 0x0
ElementFromHandle 0x80040201
```

`0x80040201` ist `UIA_E_ELEMENTNOTAVAILABLE`.

Der Root-Element-Zugriff funktioniert, `ElementFromHandle` für dieses
Python-Fenster liefert jedoch „Element nicht verfügbar“. Damit ist der
Provider weiterhin nicht als screenreader-tauglich bestätigt.


## Korrigierter Test (vollständiger HWND)

Der vorherige Test las nur das erste Zeichen des HWND (`6` statt `6229492`).

Mit vollständigem HWND:

```text
CoCreateInstance 0x0
GetRootElement 0x0
ElementFromHandle 0x0
CurrentName AMFWX UIA Probe
ControlType 50032 (Window)
FindAll 0x0
Children count 1
 child 0  (leer) 50037 (TitleBar)
```

Ergebnis:

- `ElementFromHandle` funktioniert.
- Der Client sieht den nativen Fensterrahmen (TitleBar).
- Es wird weiterhin **kein `WM_GETOBJECT`** an das Python-Fenster gesendet.
- Der Custom-Provider wird daher nicht aufgerufen.


## Durchbruch: native 1×1-Proxies

Mit nativen `STATIC`/`BUTTON`/`EDIT`-Children (1×1, transparent, no-activate)
sieht der UIA-Client jetzt:

```text
Children count 4
 child 0 Text 50020
 child 1 Aktion 50000
 child 2 Probe 50020
 child 3 TitleBar
```

Damit ist der Accessibility-Baum erstmals clientseitig sichtbar.
Der Custom-COM-Provider bleibt optional; die Proxies sind die stabile
Hosting-Schicht.


## Proxy-Aktionen

- native `BUTTON` -> `widget.activate()`
- native `BS_AUTOCHECKBOX` -> `widget.toggle()`
- native `EDIT` -> `widget.set_text()`
- `BM_CLICK` und `EN_CHANGE` getestet


## MSAA-Fallback

Native Proxies liefern über `AccessibleObjectFromWindow`:

```text
Button: name=Aktion, role=43 (ROLE_SYSTEM_PUSHBUTTON)
Edit:   role=40/42
```

Damit ist mindestens der MSAA-Weg für Screenreader sichtbar.


## MSAA-DefaultAction

`accDoDefaultAction` auf dem Proxy-Button loest den AMFWX-Callback aus:

```text
do_default_action(hwnd) -> 0
Button.on_click -> [1]
```

Damit ist der Screenreader-Bedienweg ueber MSAA grundsaetzlich vorhanden.


## Echter NVDA-Test (2026-11-21)

NVDA 2026.3.1 portable aus `D:\tools\NVDAPortable`.

Getestet mit `nvda_probe.py`:

```text
IO - speech.speech.speak:
  "AMFWX Screenreader Test"
  "Aktion, Schalter"
```

Mit Fokus auf `LineEdit`:

```text
IO - speech.speech.speak:
  "Eingabefeld, Textfeld"
```

Ergebnis: NVDA liest Fenstertitel, Button-Name/Rolle und Edit-Feld
ueber die nativen Proxies. Der MSAA-Pfad funktioniert mit einem echten
Screenreader.


## Native UIA-Patterns (2026-11-22)

`native/uia_provider.dll` (MinGW GCC 16.2.0, statisch) liefert pro Proxy:

- `IRawElementProviderSimple`
- `IInvokeProvider`
- `IValueProvider`
- `IToggleProvider`

UIA-Client:

```text
ControlType : Button
Name        : Aktion
AutomationId: amfwx-<id>
InvokePattern: True
Invoke      : clicked
```

MSAA bleibt parallel erhalten:

```text
Name/Rolle/State/Value/DefaultAction/Fokus/Selection
```

Entscheidend:

- UIA sendet `WM_GETOBJECT` mit eigenem negativen ID
- MSAA sendet `-1`, `-4`, `0`
- Diese IDs werden an den nativen MSAA-Provider durchgereicht
- alle anderen an `UiaReturnRawElementProvider`


## UIA-ValuePattern und Label

Direkt am Edit-Proxy:

```text
name          : Name
ControlType   : Edit
AutomationId  : amfwx-<id>
ValuePattern  : vorhanden
value         : alt
SetValue      : neu
```

Damit liefert der native Provider:

- Label-Name
- Edit-Rolle
- AutomationId
- ValuePattern
- SetValue
