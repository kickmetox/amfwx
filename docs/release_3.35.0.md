# AMFWX 3.35.0

AMFWX 3.35 adds an experimental S7comm client.

## New

- `S7Client`
- COTP connection
- S7 setup
- read/write DB and areas
- 246 tests

## Warning

Experimental. Test against a non-production PLC first. Wrong DB numbers
or addresses can disturb a running controller.

## Notes

- no S7-1200/1500 optimized access
- no symbolic addressing
- no hardware validation yet
- Windows-only
- unsigned installer
