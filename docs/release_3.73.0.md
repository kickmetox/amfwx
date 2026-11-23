# AMFWX 3.73.0

AMFWX 3.73 encrypts registry secrets with Windows DPAPI.

## New

- `protect` / `unprotect`
- `protect_text` / `unprotect_text`
- registry encrypts password, access_secret, token, api_key
- 317 tests

## Notes

DPAPI is user-bound. A registry copied to another Windows account cannot be
decrypted.
