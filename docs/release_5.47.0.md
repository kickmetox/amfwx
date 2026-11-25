# AMFWX 5.47.0

Timeouts for LLM app tools.

## New

- `UiSession.app_tool_timeout` (default 30 s)
- app tools run in a worker thread with a hard wait limit
- timeout result:

```json
{"ok": false, "error": "App-Tool-Timeout nach 30s"}
```

- 434 tests

## Security

A slow scanner, printer or camera cannot block an agent turn indefinitely.
The hardware call itself may still finish in the background; the agent gets a
timeout result instead.
