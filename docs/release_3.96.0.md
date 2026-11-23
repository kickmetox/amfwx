# AMFWX 3.96.0

Kyocera-style eSCL support.

## New

- HTTPS eSCL on port 9096
- `probe_escl(..., secure=...)`
- `PrinterEndpoint` scan includes 9096
- `InputSource` (Platen/Feeder)
- `ScanRegions`
- `DocumentFormat`
- `source="Feeder"` for ADF scans
- 352 tests

## Why

Scantuxio's tested Kyocera path uses `https://<ip>:9096`, not HTTP port 80. The
local Kyocera is still offline, but the scanner client now matches that path.
