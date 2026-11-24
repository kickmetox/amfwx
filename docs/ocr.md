# OCR

Windows OCR via `Windows.Media.Ocr` and optional `winsdk`.

```python
from amfwx import ocr_image, ocr_pdf

print(ocr_image("scan.jpg", language="de-DE"))
print(ocr_pdf("scan.pdf", language="de-DE"))
```

CLI:

```powershell
python -m amfwx --ocr-image scan.jpg --ocr-language de-DE
python -m amfwx --ocr-pdf scan.pdf --ocr-language de-DE
```

## Requirements

```powershell
pip install winsdk
```

A Windows OCR language pack must be installed.

## Limits

- no searchable PDF text layer yet
- no OCR during scan automatically
- layout/tables are flattened to text
