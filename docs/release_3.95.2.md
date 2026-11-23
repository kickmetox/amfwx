# AMFWX 3.95.2

Fix FRITZ!Box v2 challenge.

## Fix

- `pbkdf2_hmac(...).hexdigest()` -> `.hex()`
- v2 challenge now produces a response
- 352 tests

## Real result

Router at 192.168.178.1 speaks FRITZ!Box login, but empty/admin password is
rejected, so its host list cannot be read without credentials.
