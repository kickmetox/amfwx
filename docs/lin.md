# LIN bus

```python
from amfwx import LinFrame, PcanLin

with PcanLin() as bus:
    bus.write(LinFrame(0x10, b"\x01\x02"))
    frame = bus.read()
```

## Implemented

- `LinFrame`
- IDs 0..0x3F
- 1..8 data bytes
- PCAN-LIN backend

## Not implemented

- LIN scheduler tables
- master/slave role control
- diagnostics (UDS on LIN)
- checksum configuration
- sleep/wakeup
- LDF parsing

The PCAN-LIN backend requires `PCANBasic.dll` and a compatible adapter.

## Limits

- Windows-only
- vendor DLL required
- no hardware-in-the-loop CI
