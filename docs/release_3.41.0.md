# AMFWX 3.41.0

AMFWX 3.41 adds WIA and TWAIN scanner enumeration.

## New

- `list_wia_devices`
- `list_twain_sources`
- `WiaDevice`
- `TwainSource`
- scanners in the device inventory
- 257 tests

## Notes

- WIA needs optional `comtypes`
- TWAIN needs a matching 32/64-bit DSM
- image acquisition is not implemented yet
- Windows-only
- unsigned installer
