# AMFWX 5.31.0

32-bit runtime in CI artifacts.

## New

The CI workflow now downloads the official Python 3.12 embeddable win32
distribution and places it at `vendor/python32` before building.

This makes the CI portable ZIP and installer contain:

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

414 tests.
