# AMFWX 3.89.0

Fix the module/CLI entry point.

## Fix

- `python -m amfwx` now uses `Application`
- `--version`, `--doctor`, `--devices`, `--list-devices` work
- shared demo window factory
- 342 tests

## Root cause

`amfwx/__main__.py` still launched the old demo and ignored argv.
