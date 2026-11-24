# AMFWX 5.27.0

Becker Centronic USB receive channel.

## New

- `parse_packet`
- `BeckerStick.read_packet`
- `BeckerStick.listen`
- `--becker-listen S`
- 410 tests

## Parsed fields

```text
unit
channel
command (up/down/stop/pair/...)
increment
checksum
```

## Note

No Becker stick is connected; packet construction and parsing are tested with
generated packets and a fake serial port.
