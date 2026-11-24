# AMFWX 5.34.0

Scanner post-processing and unified dashboard.

## Scanner post-processing

- automatic deskew
- white-border crop
- blank-page removal
- optional grayscale
- integrated in eSCL ScanWindow and device ScannerWindow
- `scan_to_pdf(..., postprocess_options=...)`

## Dashboard

- `DashboardWindow`
- `--dashboard`
- scanner, printer, camera, network, USB and serial inventory
- category filter
- 419 tests

## Limitations

Deskew uses a projection-profile estimate. Crop removes white borders but does
not detect document edges in dark backgrounds.
