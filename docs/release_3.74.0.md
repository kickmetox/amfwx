# AMFWX 3.74.0

Add a graphical discovery window.

## New

- `HomeDevicesPanel`
- `HomeDevicesWindow`
- scan button
- one-click add
- registry integration
- 319 tests

## Usage

```python
from amfwx import HomeDevicesWindow, HomeRegistry

HomeDevicesWindow(HomeRegistry("devices.json")).run()
```

## Limits

- no credential dialog
- generic adapters still need paths/topics
- no device removal UI
