# AMFWX 2.4.2 – Release Notes

## Status

- Windows-only, pure Python + ctypes
- 152 automated tests
- Wheel, portable ZIP and own installer
- local Authenticode signature: `Valid`

## Schwerpunkte

### UI

- eigene Widgets, Layouts, Themes
- Editor, Tabs, Docking, Dialoge
- TableView/TreeView
- PropertyGrid, Charts
- Model/View: ListModel, TableModel, SortFilterModel
- deklarativ: State, QuickView
- Animation/Timeline

### Text

- TrueType/PNG
- GSUB/GPOS
- Arabisch/Bidi
- Textlayout, IME, Clipboard

### Accessibility

- native UIA-Provider-DLL (`uia_provider.dll`)
- `IRawElementProviderSimple`
- `IRawElementProviderFragment`
- Invoke/Value/Toggle
- Bounds/Fokus/Struktur/Namensereignisse
- MSAA parallel
- NVDA bestätigt

### Medien

- H.264/MP4 über Media Foundation
- MP4-Audio, Audio-Queue, Seek
- AVI/MJPEG
- WAV/waveOut
- MIDI
- DSP: Gain, Mixer, Biquad, Graph
- Mixer-UI und Presets

### Grafik/GPU

- eigener BGRA-Rasterizer
- Software-3D, Mipmaps, Normal Maps
- SDL3 D3D11
- D3D12 Compute
- HLSL → DXBC/DXIL

### Plattform

- ResourcePack
- CrashLogger
- PluginRegistry
- Settings
- Installer/Uninstaller

### Härtung

- Widget-Fuzzing
- Parser-Fuzzing
- Asset-Fuzzing
- Media-/Shader-Fuzzing
- Fehlerinjektion
- Snapshot-Matrix Dark/Light/High-Contrast

## Bekannte Grenzen

- keine öffentliche CA/EV-Signatur
- Windows-only
- kein VST3-Gastgeber
- Screenreader-Zertifizierung manuell
- Media Foundation/FFmpeg bleiben System-/Fremdcodecs

## Artefakte

- `dist/amfwx-2.4.2-py3-none-any.whl`
- `dist/AMFWX-Portable-2.4.2.zip`
- `dist/AMFWX-Own-Setup-2.4.2.exe`

## Tests

```text
python -m unittest discover -s tests
→ 152 Tests
```

## Härtung

```text
python tools/hardening_check.py
→ OK
```
