# AMFWX 3.52.0

AMFWX 3.52 activates the already running instance.

## New

- named activation event
- `SingleInstance(on_activate=...)`
- second process signals the first
- 271 tests

## Usage

```python
from amfwx import SingleInstance, Window
import ctypes

window = Window("AMFWX", 800, 600)

def activate():
    user32 = ctypes.windll.user32
    user32.ShowWindow(window.hwnd, 1)
    user32.SetForegroundWindow(window.hwnd)

lock = SingleInstance("AMFWX", on_activate=activate)
if not lock.acquire():
    raise SystemExit(0)
window.run()
```

## Notes

- Windows-only
- unsigned installer
