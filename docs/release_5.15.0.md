# AMFWX 5.15.0

Becker Centronic USB.

## New

- `BeckerStick`
- `becker_code`
- `list_sticks`
- `--list-becker`
- `--becker-port`
- `--becker-channel`
- `--becker-action`
- `--becker-unit`
- 396 tests

## Protocol

Serial 868 MHz stick at 115200 baud:

```text
STX + 40-char code + checksum + ETX
```

Supported commands: up, down, stop, pair, intermediate positions.

## Notes

No Becker stick was connected; code generation and serial writes are tested
with a fake serial port.
