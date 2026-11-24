# AMFWX 5.33.0

Paper size and landscape for Windows printing.

## New

- `--paper A4|A5|A3|Letter|Legal`
- `--landscape`
- DEVMODE fields:

```text
dmPaperSize
dmOrientation
```

- applies to PDF printing through the Windows queue
- 414 tests

## Examples

```powershell
python -m amfwx --print-file "scan.pdf" --printer "AMFWX Kyocera" --paper A4 --landscape
python -m amfwx --print-file "scan.pdf" --printer "AMFWX Kyocera" --paper A5 --copies 2 --duplex
```

No paper test with landscape/A5 was performed; DEVMODE values are verified.
