# AMFWX 5.25.0

Camera controls and MQTT TLS.

## Cameras

- brightness / contrast / exposure / focus in CameraWindow
- `IpCamera.set_control`
- GoPro video start/stop
- 407 tests

## MQTT

- `tls`
- `cafile`
- `certfile` / `keyfile`
- `insecure`
- Zigbee2MQTT CLI:

```powershell
python -m amfwx --zigbee-host 192.168.178.10 --zigbee-devices --zigbee-tls
python -m amfwx --zigbee-host 192.168.178.10 --zigbee-devices --zigbee-tls --zigbee-cafile ca.pem
```
