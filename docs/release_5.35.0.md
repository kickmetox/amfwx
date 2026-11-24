# AMFWX 5.35.0

SDK packaging.

## New

- `amfwx/py.typed`
- `amfwx-sdk` console entry point
- `amfwx-sdk --tools`
- `amfwx-sdk --snapshot demo.png`
- `python -m amfwx --llm-tools`
- platform wheel: `amfwx-5.35.0-py3-none-win_amd64.whl`
- 421 tests

## SDK

```powershell
pip install amfwx-5.35.0-py3-none-win_amd64.whl
amfwx-sdk --tools
amfwx-sdk --snapshot demo.png
```

## Still external

- Ollama / OpenAI-compatible endpoint
- API key
- `chip-tool`, NAPS2, gPhoto2, rtl_433 where used
- `vendor/python32` remains in the installer/portable package, not in the wheel
