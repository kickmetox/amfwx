# Bluetooth

```python
from amfwx import list_radios, list_bluetooth_devices

for radio in list_radios():
    print(radio.name, radio.address)

for device in list_bluetooth_devices():
    print(device["name"], device["address"], device["connected"])
```

## Implemented

- enumerate Bluetooth radios
- radio name/address/manufacturer
- enumerate known/remembered/connected devices
- optional inquiry
- device name/address/flags

## Not implemented

- pairing
- unpairing
- SPP serial setup
- GATT/BLE services
- audio profiles
- file transfer
- device connection control

Bluetooth SPP devices often appear as COM ports. Use `amfwx.io.SerialPort`
once Windows has created the COM port.

## Limits

- Windows-only
- inquiry can take several seconds
- no BLE/GATT yet
- no pairing UI
