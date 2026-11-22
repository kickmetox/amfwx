# AMFWX Accessibility

AMFWX exposes two accessibility paths in parallel:

1. **UI Automation (UIA)** via a native C++ provider DLL.
2. **MSAA** via the native Win32 proxy controls.

## Provider layers

```text
Window
└─ AccessibilityTree
   └─ AccessibilityNode
      ├─ role
      ├─ name
      ├─ value
      ├─ bounds
      ├─ checked/enabled/focused
      └─ actions
         ├─ activate()
         ├─ set_value()
         └─ focus()

Window
└─ AccessibilityBridge
   ├─ tree → proxy name
   ├─ tree → proxy value
   ├─ tree → checkbox state
   ├─ proxy focus → widget focus
   └─ tree → UIA bounds/events
```

## Native proxy windows

Each widget with text gets a 1×1 native proxy control:

| Widget | Proxy class | UIA control type |
|---|---|---|
| Label | STATIC | Text |
| Button | BUTTON | Button |
| CheckBox | BUTTON (auto) | CheckBox |
| LineEdit/TextEdit | EDIT | Edit |

The proxies are transparent and not part of the visual layout.

## UIA provider

`native/uia_provider.cpp` builds `uia_provider.dll` and implements:

- `IRawElementProviderSimple`
- `IRawElementProviderFragment`
- `IInvokeProvider`
- `IValueProvider`
- `IToggleProvider`

It provides:

- Name
- Control type
- Automation id
- Enabled / offscreen / focus
- Bounding rectangle
- Invoke / Value / Toggle

## WM_GETOBJECT routing

```text
MSAA: -1, -4, 0      → native MSAA provider
UIA:  other ids      → UiaReturnRawElementProvider
```

This keeps NVDA (MSAA) and UIA clients working at the same time.

## Events

- `notify_focus(hwnd)`
- `notify_structure(hwnd)`
- `notify_name(hwnd, old, new)`

## Verified

- UIA InvokePattern → AMFWX callback
- UIA TogglePattern → checkbox state
- UIA ValuePattern → edit text
- UIA label association
- UIA bounds 240×32
- NVDA speech:

```text
"AMFWX Label Test"
"Name", "Eingabefeld", "Text"
```

## Tests

```powershell
python -m unittest tests.test_a11y_proxy tests.test_accessibility tests.test_uia_native -v
```

## Known limits

- Public code-signing certificate still required.
- Some UIA clients may cache patterns; restart the client after rebuilding
  `uia_provider.dll`.
- Full screenreader certification is still manual work.
