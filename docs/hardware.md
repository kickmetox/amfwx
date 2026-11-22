# Hardware and control interfaces

## Implemented

### Serial / UART

```python
from amfwx.io import SerialPort, list_ports

print(list_ports())
with SerialPort("COM3", 115200, timeout=1.0) as port:
    port.write(b"ping\n")
    print(port.read(64))
```

Uses Win32 `CreateFileW`/`SetCommState`/`ReadFile`/`WriteFile`.

### Framing

- delimiter frames
- 4-byte little-endian length frames
- COBS encode/decode

Useful for microcontrollers and serial protocols.

### TCP / UDP

```python
from amfwx.io import TcpClient, UdpSocket

with TcpClient("192.168.1.50", 5000) as client:
    client.send(b"status\n")
    print(client.recv_until())

udp = UdpSocket(broadcast=True)
udp.send(b"discover", "255.255.255.255", 5001)
```

### Modbus TCP

```python
from amfwx.io import ModbusTCP

plc = ModbusTCP("192.168.1.10", 502, unit=1)
print(plc.read_holding_registers(0, 4))
plc.write_register(10, 1234)
```

Functions:

- read coils
- read holding registers
- write single register
- write multiple registers

## Not implemented

| Interface | Status | Reason |
|---|---|---|
| USB raw | not included | needs WinUSB/libusb driver and device-specific protocol |
| USB HID | not included | needs HID report descriptors per device |
| USB serial | works via COM | driver exposes a COM port |
| FireWire / IEEE 1394 | not supported | legacy stack, removed from modern Windows |
| AppleTalk | not supported | obsolete protocol |
| Bonjour/mDNS | not implemented | possible via UDP 5353 |
| WLAN native API | not implemented | possible via `wlanapi.dll` |
| Bluetooth native API | not implemented | pairing/SPP is device- and driver-specific |
| S7 / EtherNet/IP / OPC UA | not implemented | vendor/protocol stacks |
| CAN / LIN | not implemented | needs SocketCAN/PCAN/Vector drivers |

## WLAN and Bluetooth

Both are possible on Windows but need separate native work:

- WLAN: `WlanOpenHandle`, `WlanEnumInterfaces`,
  `WlanGetAvailableNetworkList`, profile APIs.
- Bluetooth: `BluetoothFindFirstRadio`, `BluetoothFindFirstDevice`,
  pairing APIs, SPP COM ports.

Bluetooth SPP devices often appear as COM ports and already work through
`SerialPort`.

## Microcontroller example

```python
from amfwx.io import SerialPort, encode_length_prefixed, FrameDecoder

with SerialPort("COM4", 115200) as port:
    port.write(encode_length_prefixed(b"led:on"))
    decoder = FrameDecoder(b"\n")
    while True:
        for frame in decoder.feed(port.read(64)):
            print("device:", frame)
```

## Limits

- no hardware-in-the-loop CI
- no vendor SDK
- no real-time guarantees
- no fieldbus certification
