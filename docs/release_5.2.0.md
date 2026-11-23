# AMFWX 5.2.0

MTP/PTP camera inventory and photo download.

## New

- `list_mtp_devices`
- `download_images`
- `--list-mtp`
- `--mtp-download DIR`
- `--mtp-device NAME`
- formats: JPEG, PNG, TIFF, HEIC, DNG, CR2, NEF, ARW, RAF, ORF
- 374 tests

## How

Windows Shell namespace `This PC`, filtered against PnP camera names.
Camera storage is traversed recursively; images are copied via `CopyHere`.

## Current state

No MTP camera is mounted in this session; `OsmoAction4` is visible only as a
PnP camera. The adapter is ready for MTP/PTP mode.
