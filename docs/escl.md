# eSCL / AirScan

```python
from amfwx import EsclScanner

scanner = EsclScanner("192.168.1.50", 80)
print(scanner.capabilities())
scanner.scan("scan.jpg", resolution=300, color="RGB24",
             document_format="image/jpeg")
```

## Protocol

1. `GET /eSCL/ScannerCapabilities`
2. `POST /eSCL/ScanJobs` with `ScanSettings`
3. `GET <job>/NextDocument`

## Formats

- `image/jpeg`
- `image/png`
- `image/tiff`

## Not implemented

- ADF/multi-page
- duplex
- scan regions
- color profiles
- OAuth/TLS client certificates
- WSD

## Limits

- device must support eSCL/AirScan
- no authentication
- no scanner UI
