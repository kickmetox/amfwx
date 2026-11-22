# USB HID

```python
from amfwx import list_hid_devices, HidDevice

for device in list_hid_devices():
    print(device.vendor_id, device.product_id, device.product)

with HidDevice(path) as device:
    device.write(b"\x00\x01")
    print(device.read(64))
```

## Implemented

- enumerate HID devices via SetupAPI
- vendor ID, product ID
- product/manufacturer/serial strings
- open raw HID device
- read/write reports

## Not implemented

- HID report descriptor parsing
- feature reports (`HidD_GetFeature`/`SetFeature`)
- usage pages
- raw USB bulk/interrupt endpoints
- WinUSB/libusb devices without HID
- driver installation

Raw USB devices without HID need WinUSB/libusb and a device-specific
protocol. HID devices are usable without a custom driver.

## Limits

- Windows-only
- report IDs are device-specific
- no keyboard/mouse capture (system owns input)
