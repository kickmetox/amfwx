# AMFWX 5.44.0

Camera profiles.

## New

- camera profile name field
- save/load buttons in CameraWindow
- saved fields:

```text
index, URL, width, height, folder,
frames, interval, seconds, chroma,
brightness, contrast, exposure, focus
```

- stored in `%APPDATA%\AMFWX\profiles.json`
- 432 tests

## Usage

```powershell
python -m amfwx --camera-ui
```

Enter a profile name, configure the camera, press **Profil speichern**.
