# WLAN

```python
from amfwx import list_wlan_interfaces, scan_wlan

for interface in list_wlan_interfaces():
    print(interface.description)

for network in scan_wlan():
    print(network.ssid, network.quality, network.secure,
          network.connectable)
```

## Implemented

- WLAN interfaces
- available networks
- SSID
- signal quality
- security flag
- connectable flag
- profile name

## Not implemented

- connect/disconnect
- profile creation
- password entry
- WPA enterprise
- hidden network handling
- BSSID/channel details
- roaming control

Connecting requires a WLAN profile XML and `WlanConnect`; that is a
separate, security-sensitive API.

## Limits

- Windows-only
- Windows WLAN service must be running
- scan may be empty until the adapter finishes scanning
- no BLE/mesh
