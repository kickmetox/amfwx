# AMFWX 5.31.1

Make the TWAIN32 test optional without sources.

## Fix

CI now has the 32-bit runtime, but the runner has no TWAIN sources. The test
now skips on `Twain32Error` instead of failing.

## CI

- Python 3.12 embeddable win32 is downloaded before the build
- portable ZIP and installer contain `vendor/python32`
- 414 tests
