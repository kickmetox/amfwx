# AMFWX 3.72.0

AMFWX 3.72 adds a persistent home-device registry.

## New

- `HomeRegistry`
- add discovered device
- adapter factory
- JSON save/load
- 315 tests

## Usage

```python
from amfwx import HomeRegistry, discover_home

registry = HomeRegistry("devices.json")
for device in discover_home(timeout=4.0):
    registry.add_discovered(device)
registry.save()
```

## Limits

The registry does not configure credentials or vendor-specific paths
automatically. Generic adapters still need `status_path` and `command_path`.
