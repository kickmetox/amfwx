# AMFWX 4.3.1

Self-signed TLS for the IPP client.

## Fix

- `IppPrinter(..., verify_tls=False)` default
- HTTPS 9096 no longer fails with `CERTIFICATE_VERIFY_FAILED`

## Result

Kyocera 9096 accepts the IPP POST now, but returns HTTP 404 for `/ipp/print`,
`/ipp`, `/print`, `/printer`, `/wsd` and `/`. The device does not expose a
working IPP endpoint there; Scantuxio prints through the Windows queue, not IPP.

361 tests.
