# Optionaler UIA-COM-Provider

AMFWX 0.10 enthält einen **opt-in** UIA-Provider.

```python
window.enable_uia()
```

Implementiert:

- `IRawElementProviderSimple`
- `IRawElementProviderFragment`
- `IRawElementProviderFragmentRoot`
- `IInvokeProvider` für Buttons
- `IValueProvider` für LineEdit/TextEdit
- `ISelectionProvider` für Tabellen/Bäume
- `ITextProvider`
- `ITextRangeProvider`
- Textauswahl als SAFEARRAY
- UIA-Events: Fokus, Invoke, ValueChanged
- `WM_GETOBJECT`/`UiaRootObjectId`
- `UiaReturnRawElementProvider`
- Name, ControlType, IsEnabled, IsOffscreen
- BoundingRectangle
- Parent/Child/Sibling-Navigation
- `ElementProviderFromPoint`
- Fokus

Nicht implementiert:

- UIA-Events für Text/Selection
- TextPattern
- TextPattern
- SelectionPattern
- vollständiges Property-Marshalling
- SAFEARRAY für RuntimeId/BoundingRectangle
- Inspect.exe-/Screenreader-Test

## Aktivierung

```python
window = Window("App")
window.enable_uia()
window.run()
```

Ohne `enable_uia()` wird kein Provider erzeugt und `WM_GETOBJECT`
bleibt unverändert.

## Warum opt-in?

UIA ruft aus COM-Threads. Der Provider nutzt Python-Callbacks; ein
Standardfenster soll dadurch nicht destabilisiert werden.

## Status

**Eigener COM-Provider:** ja, minimal.  
**Produktionsreif für Screenreader:** nein.  
**Nächster Schritt:** TextPattern/SelectionPattern.

## Grenzen

- keine COM-Thread-Isolation
- keine UIA-Events
- kein Text-/Value-Pattern
- keine SAFEARRAY-RuntimeId
- keine vollständige BoundingRectangle-Property
- kein automatisierter Inspect-Test
