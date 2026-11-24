# AMFWX 5.28.0

Tuya LAN discovery for 3.3–3.5.

## New

- 55AA plaintext/AES-ECB discovery
- 6699 AES-GCM discovery
- UDP 6667 broadcast
- UDP 7000 solicitation
- `--tuya-discover S`
- 413 tests

## Tested

Crafted 55AA and 6699 discovery packets are parsed correctly. No Tuya device
was available for a live broadcast test.
