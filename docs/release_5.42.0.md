# AMFWX 5.42.0

Print preview.

## New

- `PrintPreviewWindow`
- first-page preview
- A4/A5/A3/Letter/Legal
- copies
- duplex
- landscape
- `--print-preview FILE`
- 429 tests

## Usage

```powershell
python -m amfwx --print-preview "scan.pdf" --printer "AMFWX Kyocera"
```

The window renders the first page, lets the user choose paper/copies/duplex/
landscape, then sends the job through the Windows queue.

## Limits

Preview shows only the first page. Printing still uses the existing GDI path.
