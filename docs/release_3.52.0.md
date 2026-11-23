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

window = Window("AMFWX", 800, 600)
lock = SingleInstance("AMFWX", on_activate=lambda: window.invoke(
    lambda: (window.show(), window.focus())))
if not lock.acquire():
    raise SystemExit(0)
window.run()
```

## Notes

- Windows-only
- unsigned installer
