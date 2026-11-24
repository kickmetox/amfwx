# AMFWX 5.30.0

Update check against GitHub releases.

## New

- `check_update`
- `download_update`
- `is_newer`
- `pick_installer`
- `--check-update`
- `--download-update DIR`
- 414 tests

## Usage

```powershell
python -m amfwx --check-update
python -m amfwx --download-update "D:\Updates"
```

## Security

The installer is currently unsigned. The update check only reports and
downloads; it does not execute the installer automatically.
