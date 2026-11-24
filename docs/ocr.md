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

## Scan directly to searchable PDF

```powershell
python -m amfwx --scan-host 192.168.178.93 --scan-source Feeder --scan-pages 5 --scan-ocr --ocr-language de-DE
```

Output: `*_searchable.pdf` next to the raw PDF.
