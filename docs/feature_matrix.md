# AMFW vs. AMFWX – Feature-Matrix

Stand: AMFWX 1.5.4, AMFW 1.98.

| Bereich | AMFW | AMFWX 1.5.4 |
|---|---|---|
| Fenster/Eventloop | Win32 | Win32 |
| Zeichnen | GDI+ | eigener BGRA-Rasterizer |
| Rasterizer | GDI+ | eigener Rasterizer |
| Alpha/AA | GDI+ | eigenes Blending, Rounded-AA |
| Widgets | >80 | >30 |
| Layouts | Box/Grid/Form/Stack | Box/Grid/Form |
| Model/View | Modelle | ListModel/TableModel/SortFilter |
| Deklarativ | amfw.quick | QuickView/State |
| Animation | ja | Animation/Timeline |
| Text | GDI+, Unicode | TTF, Unicode, eigenes Shaping |
| Text-Shaping | GDI+ | GSUB/GPOS, Arabisch, Bidi |
| Fokus/Tastatur | ja | ja |
| LineEdit | ja | ja |
| CheckBox/Slider/ComboBox | ja | ja |
| ScrollArea | ja | ja |
| Menüs | vollständig | Basis |
| Dialoge | viele | Dialog/MessageBox |
| Dateidialoge | ja | native comdlg32 |
| TableView | bearbeitbar/Model | Sort/Resize/Multi-Select |
| TreeView | bearbeitbar/DnD | Icons/Keyboard/DnD |
| Charts | ja | ja |
| PropertyGrid | ja | ja |
| Docking | ja | Tabs/Resize/Floating/Presets |
| Touch/WM_POINTER | ja | ja |
| Gesten | ja | ja |
| DnD | intern + Dateien | intern |
| Themes | 4 + Editor | 3 + Editor |
| High Contrast | ja | ja |
| UIA/MSAA | Host/MSAA | native UIA + MSAA |
| NVDA | ja | ja |
| Video | ja | H.264/MP4, AVI/MJPEG |
| Audio | ja | WAV, MP4-Audio, Queue, Seek, MIDI, DSP |
| GPU | – | SDL3 D3D11 |
| Compute | – | D3D12 Compute |
| Shader | – | HLSL → DXBC/DXIL |
| Crash-Logging | ja | ja |
| Installer | Tooling | eigener Installer |
| PE-Analyzer | ja | nein |
| Vendor-Adapter | ja | nein |
| AMFW in AMFWX | – | `AmfwxWindowHost` |
| AMFWX in AMFW | – | `AmfwxView` |
| Gemeinsame Themes | – | `interop.py` |
| Plattformen | Windows | Windows |
| Tests | 402 | 126 |

## Koexistenz

- **AMFW hostet AMFWX:** `AmfwxView` (BGRA-Canvas als AMFW-Image).
- **AMFWX hostet AMFW:** `AmfwxWindowHost` (AMFW-Fenster als natives Child).
- **Ein Eventloop:** AMFWX pumpt die Win32-Nachrichten.
- **Themes:** `interop.from_amfw`/`to_amfwx`.

## Was AMFWX bewusst nicht ersetzt

- Crash-Logging
- PE-Analyzer
- Vendor-Adapter
- Cross-Platform
- JavaScript/Webview

## Nächste Lücke

Model/View-Architektur und deklarative UI in AMFWX.
