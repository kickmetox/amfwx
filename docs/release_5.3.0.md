# AMFWX 5.3.0

32-bit TWAIN/WIA through NAPS2, plus a complete missing-features list.

## New

- `Naps2Scanner`
- `list_naps2_sources`
- `naps2_available`
- `DeviceManager` includes NAPS2 sources
- `docs/missing.md`
- 376 tests

## 32-bit drivers

NAPS2.Console.exe handles 32-bit TWAIN and WIA drivers, like Scantuxio does.
It is optional and not bundled (GPL). Search paths:

- `PATH`
- `Program Files\NAPS2`
- `Program Files (x86)\NAPS2`
- `%LOCALAPPDATA%\Programs\NAPS2`
- `vendor\naps2`
- `AMFWX_NAPS2`

## Current state

NAPS2 is not installed on this machine, so only the adapter and tests are
present. The existing 32-bit Python TWAIN bridge remains available.
