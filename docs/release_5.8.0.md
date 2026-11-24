# AMFWX 5.8.0

32-bit TWAIN runtime is now packaged.

## Fixed

The 32-bit files were not part of the PyInstaller app or portable ZIP.

Now included:

```text
_internal/vendor/python32/
_internal/amfwx/bin/TWAINDSM32.dll
_internal/amfwx/twain32_helper.py
```

Also in `AMFWX-Portable-5.8.0.zip`.

## Verified

```text
twain32.available() -> True

CanoScan LiDE 210 (Canon Inc.)
WIA-Kyocera:ECOSYS M5521cdn:KMB5C
WIA-WIA CanoScan LiDE 210
WIA-Kyocera ECOSYS M5521cdn
```

## Installer

Silent install verified; `_internal/vendor/python32/python.exe` exists after
installation.

381 tests.
