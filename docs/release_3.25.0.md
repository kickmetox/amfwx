# AMFWX 3.25.0

AMFWX 3.25 adds display/monitor APIs for HDMI/DisplayPort/VGA outputs.

## New

- `Monitor`
- `list_monitors`
- `primary_monitor`
- `monitor_work_area`
- `move_to_monitor`
- `fullscreen` / `exit_fullscreen`
- 223 tests

## Notes

Windows exposes monitors and modes, not the physical connector.
`Monitor.adapter` is the GPU/adapter name, not HDMI/DP/VGA.

Connector-type metadata via `QueryDisplayConfig` is not implemented yet.

## Assets

- `amfwx-3.25.0-py3-none-any.whl`
- `AMFWX-Portable-3.25.0.zip`
- `AMFWX-Own-Setup-3.25.0.exe` (unsigned)
- `SHA256SUMS.txt`
