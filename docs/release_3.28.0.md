# AMFWX 3.28.0

AMFWX 3.28 adds USB HID support.

## New

- `list_hid_devices`
- `HidDevice`
- vendor/product IDs
- product/manufacturer/serial
- raw HID report read/write
- 229 tests

## Notes

- no HID report descriptor parser yet
- no feature reports yet
- raw non-HID USB needs WinUSB/libusb
- Windows-only
- unsigned installer
