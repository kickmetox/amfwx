# AMFWX 3.37.1

AMFWX 3.37.1 makes the device inventory tolerant of missing services.

## Fix

`DeviceManager.refresh()` now returns empty lists for unavailable
interfaces instead of raising. This covers WLAN service 1062, missing
Bluetooth radio, or no WinUSB devices.

## Tests

249 tests.
