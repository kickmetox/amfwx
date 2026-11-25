# AMFWX 5.43.0

Named scanner profiles.

## New

- `ProfileStore`
- scanner profile name field
- save/load buttons in ScannerWindow
- profiles stored under `%APPDATA%\AMFWX\profiles.json`
- fields: backend, source, folder, DPI, PDF, OCR, language, ADF, deskew,
  crop, blank-page removal
- 431 tests

## Usage

```powershell
python -m amfwx --scanner-ui
```

Enter a profile name, configure the scanner, press **Profil speichern**.
Select a profile and press **Profil laden**.
