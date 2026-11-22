# AMFWX 3.44.1

Fix TWAIN identity constant.

## Fix

- `DAT_IDENTITY` is 3, not 1
- TWAIN source enumeration now uses the correct data group
- 261 tests

## Notes

TWAIN image transfer remains unimplemented. The bundled DSM enumerates
sources, but this machine has no TWAIN source registered.
