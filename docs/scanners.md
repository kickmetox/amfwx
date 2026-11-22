# Scanners: WIA and TWAIN

## WIA

Optional COM automation via `comtypes`:

```powershell
pip install comtypes
```

```python
from amfwx import list_wia_devices

for device in list_wia_devices():
    print(device.name, device.device_id)
```

WIA is the modern Windows scanner API. It works for 32-bit and 64-bit
applications through COM registration.

If `comtypes` is missing or no WIA service is available, the list is empty.

## TWAIN

```python
from amfwx import list_twain_sources

for source in list_twain_sources():
    print(source.product_name, source.manufacturer)
```

The loader tries:

1. `twaindsm.dll` (TWAIN DSM 2.x, 64-bit capable)
2. `twain_32.dll` (legacy; only loadable by 32-bit Python)

A 32-bit Python process can enumerate legacy TWAIN sources; a 64-bit
Python process needs a 64-bit DSM.

## 32/64-bit

| Python | WIA | TWAIN |
|---|---|---|
| 32-bit | COM | `twain_32.dll` or DSM |
| 64-bit | COM | 64-bit `twaindsm.dll` |

`twain_32.dll` cannot be loaded into a 64-bit process. That is a Windows
architecture rule, not an AMFWX limitation.

## Not implemented

- image acquisition
- TWAIN memory/file transfer
- WIA item transfer
- ADF/duplex settings
- resolution/color settings
- scanner UI

Enumeration is implemented; actual scanning is the next step.

## Limits

- optional `comtypes` for WIA
- vendor DSM required for TWAIN 64-bit
- no hardware-in-the-loop CI
