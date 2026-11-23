# IPP printing

```python
from amfwx import IppPrinter

printer = IppPrinter("192.168.1.60")
result = printer.print_file("document.pdf")
print(result)
```

## Implemented

- IPP 2.0
- `Print-Job`
- `printer-uri`
- `requesting-user-name`
- `job-name`
- `document-format`
- PDF/JPEG/PNG/text mapping
- HTTP/HTTPS transport

## Printer attributes

```python
print(printer.get_attributes())
```

## Not implemented

- IPP Everywhere discovery details
- `Get-Printer-Attributes`
- `Get-Jobs`/`Cancel-Job`
- authentication
- TLS certificates
- job status polling
- finishers/duplex options

## Limits

- printer must accept IPP over HTTP
- document format must be supported by the device
- no print dialog
- no driver installation

## Windows queue

```powershell
python -m amfwx --list-printers
python -m amfwx --print-file scan.pdf --printer "ECOSYS M5521cdn"
```

Uses `winspool.drv` and RAW spooling. This is the path Scantuxio uses via QPrinter.
