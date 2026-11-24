# AMFWX 5.14.0

RF discovery and optional cryptography.

## New

- `rtl_433` adapter
- `jarolift_devices`
- `--rf-discovery S`
- Jarolift/Becker model filter
- cryptography is optional; Tuya 3.4/3.5 raise a clear error without it
- 393 tests

## Hardware

`rtl_433` is required for RF discovery:

```text
rtl_433 -F json -T 10
```

This covers Jarolift/Becker only when the installed rtl_433 build supports the
respective protocol. No RF hardware was available for a live test.
