# AMFWX 2.5.2

Windows-only desktop UI framework written in pure Python with `ctypes`.

## Assets

- `amfwx-2.5.2-py3-none-any.whl` â€” installable Python package
- `AMFWX-Portable-2.5.2.zip` â€” portable application
- `AMFWX-Own-Setup-2.5.2.exe` â€” self-contained installer (unsigned)
- `SHA256SUMS.txt` â€” checksums

## Highlights

- own software rasterizer and Win32 event loop
- TrueType, GSUB/GPOS, Arabic and bidi
- native UIA provider + MSAA
- H.264/MP4, audio queue/seek, MIDI, DSP
- SDL3/D3D11 and D3D12 compute
- model/view, QuickView/State, animation
- docking, charts, property grid
- plugin registry, resources, crash logging
- fuzzing and visual regression tests

## Verification

```powershell
python -m unittest discover -s tests
python tools\hardening_check.py
```

Tests: 156 passing.

## Important

- Windows 10/11 x64
- Media Foundation is used for H.264/MP4
- no public code-signing certificate is included
- the installer is intentionally unsigned; code signing is the responsibility
  of the publisher/distributor
- no cross-platform support
- no VST3 host

