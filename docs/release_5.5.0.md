# AMFWX 5.5.0

Searchable PDF through OCR.

## New

- `make_searchable_pdf`
- `--ocr-searchable IN OUT`
- invisible OCR text layer per page
- 379 tests

## Real test

Generated page text:

```text
AMFWX Searchable PDF
```

The output PDF contains extractable text:

```text
AMFWX
Searchable
PDF
```

## Requirements

- `winsdk`
- Windows OCR language pack
- `pymupdf` for PDF rendering
