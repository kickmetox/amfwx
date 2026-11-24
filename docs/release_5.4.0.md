# AMFWX 5.4.0

Windows OCR.

## New

- `ocr_image`
- `ocr_pdf`
- `--ocr-image`
- `--ocr-pdf`
- `--ocr-language`
- 378 tests

## Requirements

```powershell
pip install winsdk
```

Windows OCR language pack required.

## Real test

```text
"AMFWX OCR Test 123"
```

recognized correctly from a generated PNG.

## Limits

- no searchable PDF text layer
- no automatic OCR after scan
- layout is flattened to plain text
