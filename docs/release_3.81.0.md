# AMFWX 3.81.0

Native Somfy TaHoma / Connexoon local API.

## New

- `Tahoma`
- Bearer token
- `/setup`
- `/setup/devices/.../states`
- `/exec/apply`
- open/close/stop/position/temperature
- registry adapter
- 333 tests

## Requirements

- Developer Mode enabled
- local token generated
- port 8443
- self-signed TLS certificate

## Notes

TLS verification is disabled by default for the local self-signed gateway.
Use `verify_tls=True` with the Overkiz CA installed if needed.
