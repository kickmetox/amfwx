# AMFWX 3.29.0

AMFWX 3.29 adds mDNS/Bonjour discovery.

## New

- DNS query encoding
- DNS compression decoding
- PTR/SRV/TXT/A/AAAA parsing
- `discover_mdns`
- `Service`
- 232 tests

## Notes

- AppleTalk is obsolete and not supported
- Bonjour/mDNS is implemented at packet level
- no responder yet
- Windows-only
- unsigned installer
