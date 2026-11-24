# AMFWX 5.41.0

SDK wheel now contains the 32-bit scanner runtime.

## New

- `tools/build_sdk.py`
- `amfwx/vendor/python32` inside the wheel
- `twain32.python32_path` finds the packaged runtime
- wheel remains `win_amd64`
- 427 tests

## Verified

```python
import amfwx
from amfwx import twain32

print(amfwx.__version__)              # 5.41.0
print(twain32.available())            # True
print(twain32.python32_path())        # .../amfwx/vendor/python32/python.exe
```

The wheel grows to about 12 MB because it now ships the 32-bit runtime.

## Installer / Portable

Both still contain `_internal/vendor/python32/python.exe`.
