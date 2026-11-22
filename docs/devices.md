# Device inventory

```python
from amfwx import list_devices

devices = list_devices()
for kind, items in devices.items():
    print(kind, len(items))
```

Keys:

- `serial`
- `hid`
- `usb`
- `bluetooth`
- `wlan`
- `displays`

`DeviceManager` keeps a snapshot:

```python
from amfwx import DeviceManager

manager = DeviceManager().refresh()
print(manager.summary())
print(manager.get("hid"))
```

## Notes

Bluetooth uses known/remembered devices, not a new inquiry.
USB raw only lists devices bound to WinUSB.
Display entries are monitors, not physical connectors.
