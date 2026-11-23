# Home automation

## Real protocol clients

### Shelly Gen1/Gen2/Gen3

```python
from amfwx import ShellyDevice

shelly = ShellyDevice("192.168.178.40")
print(shelly.status())
shelly.open_cover()
shelly.set_cover_position(50)
shelly.set_light(True, brightness=70)
shelly.set_thermostat(21.5)   # Shelly TRV
```

### Fibaro Home Center

```python
from amfwx import FibaroHomeCenter

center = FibaroHomeCenter("192.168.178.50", 80, "admin", "password")
print(center.devices())
center.open_cover(12)
center.set_temperature(8, 21.0)
```

### Jarolift 433 MHz bridge

```python
from amfwx import JaroliftBridge

bridge = JaroliftBridge("192.168.178.60", base_topic="jarolift")
bridge.up("A1B2")
bridge.stop("A1B2")
```

Publishes to:

```text
jarolift/<channel>/set
{"command": "UP"}
```

### WLAN

```python
from amfwx import WlanController
WlanController().connect("MyWLAN")
```

## Generic HTTP adapter

For systems whose local API is device-specific or undocumented:

```python
from amfwx import GenericHttpDevice

device = GenericHttpDevice(
    "http://192.168.178.70",
    status_path="/api/status",
    command_path="/api/command",
)
device.open_cover()
```

Use this for:

- Becker CentralControl CC41/CC51
- Rademacher HomePilot
- Somfy TaHoma/Connexoon
- Eve over a Matter/Thread bridge
- `seve` (identity unresolved – Eve or other vendor)

**These are not protocol-verified implementations.** The endpoints and payloads
must match the device/bridge.

## Discovery window

```powershell
python -m amfwx --devices --registry devices.json
```


```python
from amfwx import HomeDevicesWindow, HomeRegistry

HomeDevicesWindow(HomeRegistry("devices.json")).run()
```

## CLI control

```powershell
python -m amfwx --list-devices --registry devices.json
python -m amfwx --device Lamp --action on --registry devices.json
python -m amfwx --device Rollladen --action close --registry devices.json
```

## Credentials

```python
from amfwx import CredentialsDialog

credentials = CredentialsDialog.ask(parent, "Fibaro-Zugangsdaten")
# {'username': ..., 'password': ...}
```

Fibaro devices prompt automatically when added from the discovery window.

## Remove / update

```python
registry.update(device_id, password="secret")
registry.remove(device_id)
```

## Registry / add

```python
from amfwx import HomeRegistry, discover_home

registry = HomeRegistry("devices.json")
for found in discover_home(timeout=4.0):
    entry = registry.add_discovered(found)
    print(entry["id"], entry["kind"])
registry.save()

adapter = registry.adapter(entry["id"])
```

## Automatic discovery

```python
from amfwx import discover_home

for device in discover_home(timeout=4.0):
    print(device.kind, device.name, device.host)
```

Implemented sources:

| Source | State |
|---|---|
| mDNS/Bonjour | ✅ |
| SSDP | ✅ |
| HTTP fingerprint | ✅ Shelly, Fibaro, Tasmota, Reolink, HomePilot, TaHoma |
| FRITZ!Box host list | ✅ |
| KNXnet/IP search | ✅ best effort |
| Tuya broadcast | ✅ detects encrypted/JSON responses |
| Bluetooth | inventory only |
| Reolink | only fingerprint |
| CCU | fingerprint not yet |

HTTP probing only detects devices; it does not add them automatically. A UI
"add" action still has to create the matching adapter config.

## Not implemented

- Becker CC41/CC51 native API
- Rademacher HomePilot native API
- Somfy TaHoma OAuth/token flow
- Matter/Thread commissioning
- Eve native Matter
- Tuya LAN AES protocol
- Zigbee2MQTT/MQTT subscriptions
- Reolink control
- KNX group read/write

## Security

Credentials are per object and not persisted. Do not use over untrusted
networks.
