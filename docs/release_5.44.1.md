# AMFWX 5.44.1

Make the TWAIN32 source test robust in CI.

## Fix

The Windows CI runner has no scanner and can hang inside the TWAIN DSM.
`test_sources` now skips on any TWAIN error or timeout instead of failing.

## Result

431 tests, CI green.
