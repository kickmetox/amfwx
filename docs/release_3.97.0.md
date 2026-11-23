# AMFWX 3.97.0

Kyocera-style ADF termination.

## New

- one-job-per-page fallback
- `ScannerStatus/AdfState` check after 404
- job deletion between pages
- 353 tests

## Behavior

- multi-page job: repeated `NextDocument`
- one-page-per-job: 404 + `ScannerAdfLoaded` -> new job
- 404 + `ScannerAdfEmpty` -> stack complete
