# Displays, HDMI, DisplayPort, VGA

Windows software does not address the physical connector directly. It sees:

- display adapters
- monitors
- modes (resolution, refresh, bit depth, orientation)
- window placement and fullscreen

## Implemented

```python
from amfwx import list_monitors, primary_monitor

for monitor in list_monitors():
    print(monitor.name, monitor.width, monitor.height,
          monitor.refresh, monitor.primary)

primary = primary_monitor()
```

Window placement:

```python
from amfwx import fullscreen, exit_fullscreen, move_to_monitor

fullscreen(window)                 # primary monitor
move_to_monitor(window, monitor)   # normal window on monitor
exit_fullscreen(window)
```

`monitor_work_area(window)` returns the usable area without taskbar.

## Connector types

HDMI, DisplayPort, VGA, DVI and USB-C are **physical connectors**.
Windows normally exposes them as monitor outputs, not as an API named
"HDMI". The adapter string in `Monitor.adapter` is the GPU/adapter name,
not the cable type.

A connector-type query would require `QueryDisplayConfig` and
`DISPLAYCONFIG_TARGET_DEVICE_NAME.outputTechnology`; that is not
implemented yet.

## What is not a display API

- HDMI audio routing
- HDCP
- EDID parsing
- DisplayPort MST topology
- VGA mode setting
- capture cards / HDMI input

Capture cards and HDMI input need Media Foundation or a vendor SDK.

## Safe behavior

`fullscreen()` stores the previous rectangle and style. `exit_fullscreen()`
restores them. Resolution changes are not performed automatically.

## Limits

- Windows-only
- no EDID/connector metadata yet
- no capture input
- no HDR control
- no per-monitor DPI API wrapper yet
