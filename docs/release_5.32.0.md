# AMFWX 5.32.0

Matter dimming and color temperature.

## New

- `MatterController.level`
- `MatterController.color_temperature`
- `--matter-level N`
- `--matter-temperature MIREDS`
- 414 tests

## Usage

```powershell
python -m amfwx --matter-node 7 --matter-level 50
python -m amfwx --matter-node 7 --matter-temperature 370
```

Requires `chip-tool`. No Matter hardware was available.
