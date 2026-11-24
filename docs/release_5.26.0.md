# AMFWX 5.26.0

Jarolift control through the ESP32 Jarolift Controller.

## New

- `JaroliftController`
- MQTT commands UP / DOWN / STOP / SHADE
- group commands
- position 0–100
- status topic
- `--jarolift-host`
- `--jarolift-channel`
- `--jarolift-action`
- `--jarolift-position`
- 409 tests

## Architecture

The ESP32 + CC1101 handles the 433 MHz KeeLoq radio layer. AMFWX talks to it
over MQTT:

```text
ESP32-Jarolift-Controller/cmd/shutter/3  -> UP
ESP32-Jarolift-Controller/cmd/position/3 -> 45
ESP32-Jarolift-Controller/status/shutter/3
```

## Note

No ESP32 Jarolift controller was available for a live test. Topic/payload
construction is tested with a fake MQTT client.
