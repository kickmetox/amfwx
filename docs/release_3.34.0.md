# AMFWX 3.34.0

AMFWX 3.34 adds raw USB via WinUSB.

## New

- `list_usb_devices`
- `WinUsbDevice`
- `UsbDeviceInfo`
- raw pipe read/write
- 243 tests

## Notes

- device must use WinUSB driver
- pipe IDs are device-specific
- no descriptor tree/config selection
- Windows-only
- unsigned installer
