# AMFWX 5.29.0

NAPS2 portable installer.

## New

- `download_naps2`
- `pick_asset`
- `--install-naps2 DIR`
- 414 tests

## Usage

```powershell
python -m amfwx --install-naps2 "D:\Tools\naps2"
```

Downloads the latest NAPS2 portable win-x64 ZIP, extracts it and prints the
`NAPS2.Console.exe` path.

## Licensing

NAPS2 is GPL and remains a separate optional download. It is not bundled in the
MIT package.
