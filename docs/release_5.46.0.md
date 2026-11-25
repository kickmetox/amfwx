# AMFWX 5.46.0

Hardening block.

## Packaging

- optional extras:
  - `scanner`
  - `camera`
  - `ocr`
  - `pdf`
  - `iot`
  - `full`
- SDK wheel still includes `vendor/python32`

## CI

- test matrix: Python 3.10, 3.11, 3.12, 3.13
- build job depends on the matrix
- snapshot baseline pinned to Python 3.12
- hardware smoke script:

```powershell
python tools/hardware_smoke.py
```

## Docs

- `docs/missing.md` updated to 5.46.0
- optional extras documented
- 433 tests
