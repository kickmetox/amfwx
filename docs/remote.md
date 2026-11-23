# Remote and IoT control

```python
from amfwx import DeconzClient, FritzBox, TuyaCloud, WlanController
```

## FRITZ!Box – TR-064

```python
box = FritzBox("192.168.178.1", "router-password")
box.login()
print(box.hosts())
print(box.wlan_info())
box.wlan_enable(False)
```

Implemented:

- login (`login_sid.lua`, MD5 and PBKDF2 challenge)
- `hosts`
- `wlan_info`
- `wlan_enable`

Not implemented:

- smart-home switches
- port forwarding
- call lists
- TR-064 over HTTPS

## Zigbee – deCONZ

```python
zigbee = DeconzClient("192.168.178.20", 80, "API-KEY")
print(zigbee.lights())
zigbee.on(1, brightness=200)
zigbee.off(1)
```

deCONZ REST API only. Zigbee2MQTT/MQTT and direct coordinators are not implemented.

## Tuya Cloud

```python
tuya = TuyaCloud("access-id", "access-secret", uid="user-id")
print(tuya.devices())
tuya.switch("device-id", True)
```

Requirements:

- Tuya IoT Platform access ID and secret
- correct data center URL (`openapi.tuyaeu.com`, `tuyus.com`, ...)
- user ID

The local Tuya LAN protocol (port 6668, AES with localKey) is **not** implemented.

## WLAN – Windows netsh

```python
wlan = WlanController()
print(wlan.current())
wlan.connect("MyWLAN")
wlan.disconnect()
```

Implemented:

- interfaces
- current SSID
- connect
- disconnect
- profiles
- visible networks

Admin rights may be required for adapter-level changes.

## Bluetooth

Bluetooth is currently **inventory only** (`list_bluetooth_devices`). Pairing,
audio routing and remote control are not implemented.

## Security

- credentials are passed per object, not persisted
- no TLS certificate pinning
- no secret storage
- use only on trusted networks
