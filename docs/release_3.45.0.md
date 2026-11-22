# AMFWX 3.45.0

TWAIN enumeration is now ABI-correct and functional.

## Fix

- TWAIN `TW_STR32` is ANSI `char[34]`, not UTF-16
- application identity is passed to `OPENDSM`
- `OPENDSM` succeeds
- `GETFIRST` returns `TWRC_ENDOFLIST` when no source is installed
- 261 tests

## Status

No TWAIN source is registered on this machine. TWAIN image transfer is
still not implemented.
