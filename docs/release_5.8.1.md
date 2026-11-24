# AMFWX 5.8.1

Make the 32-bit runtime optional for CI builds.

## Fix

- `vendor/python32` is added only when present
- CI checkouts (vendor ignored) build without it
- local release builds still include:

```text
_internal/vendor/python32/python.exe
_internal/amfwx/bin/TWAINDSM32.dll
_internal/amfwx/twain32_helper.py
```

## Verified

```text
install=0
AMFWX.exe=True
python32=True
```

381 tests.
