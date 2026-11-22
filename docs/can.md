# CAN bus

```python
from amfwx import CanFrame, PcanBus

with PcanBus() as bus:
    bus.write(CanFrame(0x123, b"\x01\x02"))
    frame = bus.read()
    print(frame.identifier, frame.data)
```

## Implemented

- `CanFrame`
- standard/extended IDs
- RTR flag
- 0..8 data bytes
- PCAN backend (`PCANBasic.dll`)

## Not implemented

- LIN
- SocketCAN
- Vector/Kvaser backends
- CANopen
- J1939
- ISO-TP
- bus arbitration/error frames
- filters

The PCAN backend requires the vendor DLL and a PEAK adapter.
Without the DLL, `CanError` is raised.

## Limits

- Windows-only
- vendor driver required
- no hardware-in-the-loop CI
