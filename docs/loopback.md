# Loopback serial

For tests without hardware:

```python
from amfwx.io import LoopbackSerial

first, second = LoopbackSerial.pair()
first.write(b"ping")
assert second.read(4) == b"ping"
```

`LoopbackSerial(echo=True)` echoes writes back to itself.

Use it with `FrameDecoder` and `ModbusRTU(transport=...)` to test
protocols without a COM port.

## Limits

- in-memory only
- no timing/baud simulation
- no error/parity injection
- no flow control
