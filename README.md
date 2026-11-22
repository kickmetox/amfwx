# AMFWX

**AMFWX** is a Windows-only desktop UI framework written in pure Python
using `ctypes`. It is not a Qt/GTK/wx/Tkinter wrapper and does not embed a
browser engine.

**Version:** 3.47.0  
**License:** MIT  
**Platform:** Windows 10/11, x86-64  
**Tests:** 266 passing

## Features

### UI

- own BGRA software rasterizer
- widget tree, box/grid/form layouts
- own Win32 event loop
- buttons, labels, edits, lists, trees, tables
- tabs, tooltips, charts, property grid
- docking, splitters, status bar, toolbar
- editor with undo/redo, find/replace
- themes: dark, light, high contrast
- animation/timeline
- declarative `QuickView` with `State`

### Text and images

- TrueType parser/rasterizer
- GSUB ligatures, GPOS pair/mark/class
- Arabic shaping and bidi
- PNG, baseline JPEG
- WebP via own `libwebp` build
- scaled PNG snapshots

### Accessibility

- native UIA provider DLL (`uia_provider.dll`)
- `IRawElementProviderSimple`
- `IRawElementProviderFragment`
- Invoke / Value / Toggle patterns
- bounding rectangles
- focus, structure and name events
- MSAA fallback
- verified with NVDA

### Media

- H.264/MP4 via Media Foundation
- MP4 metadata parser
- MP4 audio, audio queue and seek
- AVI/MJPEG
- WAV playback
- MIDI parser/player
- DSP: gain, mixer, biquad, graph
- mixer UI and JSON presets

### Graphics

- SDL3 D3D11 backend
- D3D12 compute
- HLSL to DXBC/DXIL
- software 3D renderer with textures, mipmaps and normal maps

### Platform

- settings
- resource packs
- crash logger
- plugin registry
- own installer/uninstaller
- reproducible native DLL builds

## Install

```powershell
python -m pip install dist\amfwx-2.5.0-py3-none-any.whl
```

Or run the portable build:

```text
dist\AMFWX-Portable-2.5.0.zip
```

## Test

```powershell
python -m unittest discover -s tests
python tools\hardening_check.py
```

## Native dependencies

The repository ships self-built Windows DLLs:

- `SDL3.dll` â€” built from SDL3 source
- `libwebp.dll` / `libsharpyuv.dll` â€” built from libwebp source
- `mfdecode.dll` â€” Media Foundation helper, built with MSVC
- `uia_provider.dll` â€” UIA provider, built with MinGW GCC

Build instructions:

- [SDL3 build](docs/sdl3_build.md)
- [WebP build](docs/webp_build.md)
- [UIA provider build](docs/uia_provider_build.md)
- [Media Foundation](docs/mfvideo.md)

## Limitations

- Windows-only
- code signing is the responsibility of the publisher/distributor
- no complete screenreader certification
- Media Foundation remains a system codec
- no VST3 host

## Documentation

- [Accessibility](docs/accessibility.md)
- [Framework review](docs/framework_review.md)
- [Feature matrix](docs/feature_matrix.md)
- [Distribution and signing](docs/distribution.md)
- [AMFW interop](docs/amfw_interop.md)
- [AMFW merge strategy](docs/amfw_merge.md)
- [AI/SDK integration](docs/ai_sdk.md)
- [Gap analysis](docs/gaps.md)
- [PDF export](docs/pdf.md)
- [Designer](docs/designer.md)
- [Declarative Quick](docs/quick.md)
- [Database and network](docs/db_net.md)
- [Studio / project starter](docs/studio.md)
- [RichText](docs/richtext.md)
- [Tkinter compat](docs/compat_tkinter.md)
- [wxWidgets compat](docs/compat_wx.md)
- [GTK compat](docs/compat_gtk.md)
- [JUCE compat](docs/compat_juce.md)
- [Qt compat](docs/compat_qt.md)
- [MCP](docs/mcp.md)
- [Screenreader checklist](docs/screenreader_checklist.md)
- [Form validation](docs/validation.md)
- [Hardware interfaces](docs/hardware.md)
- [Displays](docs/display.md)
- [Bluetooth](docs/bluetooth.md)
- [WLAN](docs/wlan.md)
- [USB HID](docs/usb.md)
- [USB/Thunderbolt](docs/usb_thunderbolt.md)
- [Medical data](docs/medical.md)
- [Scanners: WIA/TWAIN](docs/scanners.md)
- [Network printers/scanners](docs/network_scan.md)
- [Raw USB/WinUSB](docs/usb_raw.md)
- [mDNS/Bonjour](docs/mdns.md)
- [EtherNet/IP](docs/enip.md)
- [CAN bus](docs/can.md)
- [S7comm](docs/s7.md)
- [OPC UA](docs/opcua.md)
- [Device inventory](docs/devices.md)
- [Loopback serial](docs/loopback.md)
- [LIN bus](docs/lin.md)
- [Release notes](docs/release_2.4.2.md)

## License

MIT â€” see [LICENSE](LICENSE).

Third-party components keep their own licenses; see the license files in
`amfwx/bin/`.

