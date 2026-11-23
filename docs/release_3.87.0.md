# AMFWX 3.87.0

Tuya LAN protocol 3.3 client.

## New

- `TuyaLocal`
- AES-128-ECB with MD5(localKey)
- DP query
- DP control / switch
- optional `cryptography`
- 340 tests

## Requirements

```powershell
pip install cryptography
```

## Limits

- protocol 3.3 only
- no 3.4/3.5
- no DP metadata
- no device discovery/decryption
- tested against a local TCP mock, not real Tuya hardware
