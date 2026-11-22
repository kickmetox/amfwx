# EtherNet/IP

## ListIdentity discovery

```python
from amfwx import list_enip_identity, discover_enip

for device in list_enip_identity("192.168.1.10"):
    print(device.product_name, device.vendor_id, device.host)

for device in discover_enip(timeout=2.0):
    print(device)
```

## Implemented

- EtherNet/IP ListIdentity
- UDP port 44818
- vendor/device/product/revision/serial
- product name
- IP/port
- broadcast discovery

## Not implemented

- CIP explicit messaging
- implicit I/O
- class/instance/attribute services
- tag read/write
- PLC-specific profiles
- safety profiles

ListIdentity is discovery only. Reading PLC tags requires CIP
explicit messaging and a device-specific path.

## Limits

- broadcast may be blocked
- no routing across subnets
- no EDS parsing
