# AMFWX 5.0.0

Camera and webcam support.

## New

- `list_pnp_cameras` (Windows PnP inventory)
- `Webcam` via optional OpenCV
- camera controls (brightness, contrast, exposure, focus, ...)
- `Webcam.tether`
- `GoProCamera` HTTP control
- `GPhoto2Camera` adapter for DSLRs
- `chroma_key`, `composite`, `save_chroma`
- `--list-cameras`
- 370 tests

## Real inventory

```text
None: OsmoAction4
```

The DJI camera is visible as a PnP camera. OpenCV could not open it as a UVC
webcam in this session.

## Vendor reality

Canon, Nikon, Sony, Fuji, Olympus and Leica are covered through optional
libgphoto2/gPhoto2, not bundled vendor SDKs. GoPro uses its HTTP API. DJI works
through UVC only when the camera exposes webcam mode.

## Note

`amfwx.Camera` remains the existing 3D camera class. The webcam class is
`amfwx.Webcam`.
