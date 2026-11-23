# AMFWX 5.0.1

Camera test optional without Pillow.

## Fix

- skip `tests/test_camera.py` when Pillow is missing
- 370 tests locally, 4 skipped on CI
- camera/chroma code remains optional

## Camera coverage

- PnP inventory (includes `OsmoAction4`)
- Webcam/UVC via optional OpenCV
- controls and tethering
- GoPro HTTP
- gPhoto2 DSLR adapter
- chroma key
