# AMFWX 5.1.0

Camera window with snapshot and tethering.

## New

- `CameraWindow`
- `--camera-ui`
- index / width / height
- target folder
- frames / interval
- chroma key toggle
- 372 tests

## Notes

The camera itself must be reachable as a UVC device. The DJI OsmoAction4 is
currently only visible as a PnP camera and does not expose a UVC stream.
