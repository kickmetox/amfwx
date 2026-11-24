# AMFWX 5.17.0

Matter commissioning through chip-tool.

## New

- `MatterController`
- `commission`
- `on` / `off` / `toggle`
- `read_onoff`
- `--matter-code`
- `--matter-node`
- `--matter-action`
- 400 tests

## Requirement

`chip-tool` from connectedhomeip must be installed and available on `PATH`.
AMFWX does not bundle a Matter stack.

## Notes

No Matter hardware was available; command construction is tested with a fake
runner.
