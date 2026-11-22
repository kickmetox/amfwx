# MSAA/IAccessible-Bridge

`Window.enable_msaa()` aktiviert einen eigenen MSAA-Provider.

## Implementiert

- `IAccessible` + `IDispatch`-Vtable
- virtuelles Kindmodell
- `accChildCount`
- `accName`
- `accRole`
- `accState`
- `accLocation`
- `accHitTest`
- `accNavigate`
- `accDoDefaultAction`
- `LresultFromObject` für `OBJID_CLIENT`

## Direkter Test

```text
childCount 2
child 1 "Hallo" Rolle 42
```

## Externer Test

`AccessibleObjectFromWindow(OBJID_CLIENT)` liefert weiterhin:

```text
childCount 0
```

Der native Fenster-Provider wird also weiterhin bevorzugt.

## Warum

Auch MSAA bekommt das Top-Level-HWND über den nativen Fenster-Provider.
Ein `WM_GETOBJECT`-Return reicht hier nicht, solange der Client den
Custom-Provider nicht übernimmt.

## Nächster Weg

- native Child-HWNDs pro Widget
- oder ein echter UIA/MSAA-Host, der den Custom-Provider einhängt
