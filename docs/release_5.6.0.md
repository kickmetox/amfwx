# AMFWX 5.6.0

Scan directly to a searchable PDF.

## New

- `--scan-ocr`
- scan → PDF → OCR text layer
- output `*_searchable.pdf`
- `--ocr-language`
- 380 tests

## Usage

```powershell
python -m amfwx --scan-host 192.168.178.93 --scan-source Feeder --scan-pages 5 --scan-ocr --ocr-language de-DE
```

## Requirements

- winsdk + Windows OCR language pack
- pymupdf
