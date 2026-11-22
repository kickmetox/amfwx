# Raw USB / WinUSB

```python
from amfwx import list_usb_devices, WinUsbDevice

for device in list_usb_devices():
    print(device.vendor_id, device.product_id)

with WinUsbDevice(path) as device:
    device.write(pipe_id=0x01, data=b"\x01\x02")
    print(device.read(pipe_id=0x81, size=64))
```

## Implemented

- enumerate USB device interfaces
- WinUSB initialize/free
- device descriptor (VID/PID/class)
- raw pipe read/write
- caller-supplied pipe IDs

## Requirements

- device must use the WinUSB driver
- correct pipe IDs from the device's endpoints
- no HID report layer

## Not implemented

- automatic pipe discovery
- descriptor tree parsing
- configuration selection
- interface/alt-setting selection
- isochronous transfers
- libusb compatibility

HID devices use `amfwx.usb` instead of this module.

## Limits

- Windows-only
- driver installation is not automated
- no hardware-in-the-loop CI
