# eSCL / AirScan

```python
from amfwx import EsclScanner

scanner = EsclScanner("192.168.1.50", 80)
# Kyocera eSCL often uses HTTPS on port 9096:
# scanner = EsclScanner("192.168.1.50", 9096, secure=True)
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

## Kyocera

Many Kyocera ECOSYS devices expose eSCL on `https://<ip>:9096`.
Use `EsclScanner(host, 9096, secure=True)` and `source="Feeder"` for ADF.

## ADF termination

- multi-page job: repeated `NextDocument`
- Kyocera one-job-per-page: after 404, `ScannerStatus/AdfState` is checked; if loaded, a new job is created

## Verified hardware

Kyocera ECOSYS M5521cdn at `192.168.178.93`:

- HTTP eSCL: port `9095`
- HTTPS eSCL: port `9096`
- platen and ADF
- resolutions 200/100/400/300/600
- real scan: 1654x2337 JPEG, 217958 bytes (content deleted after the test)
