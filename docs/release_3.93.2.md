# AMFWX 3.93.2

Fix single-instance lock release in CLI paths.

## Fix

- `--list-devices` releases the mutex
- `--device/--action` releases the mutex
- `--devices` releases the mutex
- 347 tests

## Symptom

After a CLI list/control command, the next CLI invocation silently exited with
code 0 because the `AMFWX` mutex was still held.
