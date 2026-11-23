# AMFWX 3.79.0

Native Rademacher HomePilot client.

## New

- `HomePilot`
- salt/login
- devices and states
- open/close/stop/position
- on/off/temperature
- registry adapter
- 328 tests

## Protocol

Local REST API:

- `POST /authentication/password_salt`
- `POST /authentication/login`
- `GET /devices`
- `GET /v4/devices?devtype=...`
- `PUT /devices/{id}`

## Notes

Implementation follows the public `pyrademacher` client behavior. Not tested
against real HomePilot hardware here.
