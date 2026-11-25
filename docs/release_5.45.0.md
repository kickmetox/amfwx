# AMFWX 5.45.0

Hardware-free block: camera plugins, dashboard actions, print profiles, PDF text.

## Camera plugins

- `CameraDriver`
- `WebcamDriver`
- `IpCameraDriver`
- `register_camera_driver`
- `unregister_camera_driver`
- `list_camera_drivers`
- `create_camera_driver`
- entry point group `amfwx.cameras`

## Dashboard

- **Scanner** opens the scanner window
- **Kamera** opens the camera window
- **Druckvorschau** opens the print preview with a selected PDF

## Print profiles

- named print profiles
- paper, copies, duplex, landscape
- stored in `%APPDATA%\AMFWX\profiles.json`

## PDF text

- `pdf_extract_text`
- `--pdf-text IN`
- `--pdf-text-out FILE`

433 tests.
