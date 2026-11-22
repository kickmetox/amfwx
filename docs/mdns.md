# mDNS / Bonjour

```python
from amfwx import discover_mdns

for service in discover_mdns("_http._tcp.local", timeout=2.0):
    print(service.name, service.host, service.port)
```

## Implemented

- DNS query encoding
- DNS name compression decoding
- PTR/SRV/TXT/A/AAAA record parsing
- mDNS service discovery over UDP 5353

## AppleTalk vs Bonjour

AppleTalk is obsolete and not supported. Bonjour/mDNS is the modern
Apple service-discovery protocol and is implemented here at the packet
level.

## Not implemented

- full DNS-SD resolution (SRV/A/AAAA correlation across packets)
- mDNS responder (announcing services)
- unicast DNS-SD
- Wide-Area Bonjour
- AirPlay/RAOP

## Limits

- best-effort discovery
- depends on multicast support
- no firewall exception
- no cache
