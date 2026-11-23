# AMFWX 4.1.0

Scan directly to multi-page PDF.

## New

- `images_to_pdf`
- `scan_to_pdf`
- `--scan-pdf PATH`
- 359 tests

## Real Kyocera test

Platen, 200 dpi, RGB24:

- PDF 1.4
- 435967 bytes

The PDF was deleted after verification because it contained personal data.

## Notes

- JPEG pages are embedded with `DCTDecode`
- multi-page PDF
- no OCR
