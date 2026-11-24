# AMFWX 5.9.0

Zigbee2MQTT support.

## New

- `Zigbee2Mqtt`
- `devices`
- `state`
- `set`
- `permit_join`
- `--zigbee-host`
- `--zigbee-port`
- `--zigbee-devices`
- `--zigbee-set`
- `--zigbee-permit`
- 384 tests

## Usage

```powershell
python -m amfwx --zigbee-host 192.168.178.10 --zigbee-devices

python -m amfwx --zigbee-host 192.168.178.10 --zigbee-set "lamp={\"state\":\"ON\"}"

python -m amfwx --zigbee-host 192.168.178.10 --zigbee-permit 60
```

## Notes

Uses raw MQTT 3.1.1, QoS 0, no TLS. A local broker is required.
