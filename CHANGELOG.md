# Changelog

## 3.47.0 - 2026-11-23

Netzwerk-Scanner/Drucker.

### Network

* mDNS-Discovery.
* eSCL-Probe.
* `zeroconf` optional.
* 266 Tests.

## 3.46.0 - 2026-11-23

32-Bit-TWAIN-Bruecke.

### Scanners

* `list_twain32_sources`.
* `scan_twain32`.
* Canon CISDS.DS getestet.
* 263 Tests.

## 3.45.0 - 2026-11-23

TWAIN-Enumeration funktionsfaehig.

### Scanners

* ANSI-Strings korrigiert.
* Application Identity.
* OPENDSM/GETFIRST korrekt.
* 261 Tests.

## 3.44.2 - 2026-11-23

TWAIN-ABI korrigiert.

### Fix

* `DSM_Entry` DAT/MSG als 16-Bit.
* TWAIN-Strukturen `pack(2)`.
* DSM wird fuer Enumeration geoeffnet.
* 261 Tests.

## 3.44.1 - 2026-11-23

TWAIN-Konstante korrigiert.

### Fix

* `DAT_IDENTITY` = 3.
* TWAIN-Enumeration nutzt die korrekte Data Group.
* 261 Tests.

## 3.44.0 - 2026-11-23

WIA-ADF/Optionen.

### Scanners

* DPI/Farbe/Duplex.
* Mehrseiten.
* 261 Tests.

## 3.43.0 - 2026-11-23

WIA-Bildaufnahme.

### Scanners

* `WiaScanner`.
* PNG/JPEG/BMP/TIFF.
* DPI.
* 259 Tests.

## 3.42.0 - 2026-11-23

TWAIN DSM gebundelt.

### Scanners

* Offizielle TWAINDSM 2.5.1 (32/64).
* LGPL-Hinweis.
* `dsm_available`/`dsm_path`.
* 258 Tests.

## 3.41.0 - 2026-11-23

Scanner-Enumeration.

### Hardware

* WIA-Enumeration.
* TWAIN-Enumeration.
* 32/64-Bit-Doku.
* 257 Tests.

## 3.40.0 - 2026-11-23

Medizin-Datenstandards.

### Data

* HL7 v2 Parser.
* FHIR JSON.
* DICOM-Header.
* 255 Tests.

## 3.39.0 - 2026-11-22

Loopback-Serial.

### IO

* `LoopbackSerial`.
* Hardwarefreie Protokolltests.
* 252 Tests.

## 3.38.0 - 2026-11-22

Hardware-Diagnose.

### Tools

* `tools/hardware_check.py`.
* CI-Hardwarebericht.
* 250 Tests.

## 3.37.1 - 2026-11-22

Device-Inventory robust.

### Fix

* Fehlende Dienste liefern leere Listen.
* 249 Tests.

## 3.37.0 - 2026-11-22

Geraeteuebersicht.

### Platform

* `DeviceManager`.
* `list_devices`.
* 249 Tests.

## 3.36.0 - 2026-11-22

Optionales OPC UA.

### IO

* `OpcUaClient`.
* `asyncua` optional.
* 247 Tests.

## 3.35.0 - 2026-11-22

S7comm (experimentell).

### IO

* COTP/S7 Setup.
* DB lesen/schreiben.
* 245 Tests.

## 3.34.0 - 2026-11-22

Raw USB/WinUSB.

### Platform

* USB-Enumeration.
* Pipe-I/O.
* 243 Tests.

## 3.33.0 - 2026-11-22

LIN.

### IO

* `LinFrame`.
* PCAN-LIN-Backend.
* 241 Tests.

## 3.32.0 - 2026-11-22

CAN.

### IO

* `CanFrame`.
* PCAN-Backend.
* 239 Tests.

## 3.31.0 - 2026-11-22

EtherNet/IP ListIdentity.

### Network

* Geräte-Discovery.
* 237 Tests.

## 3.30.0 - 2026-11-22

Modbus RTU.

### IO

* RTU-Client.
* CRC16.
* 235 Tests.

## 3.29.0 - 2026-11-22

mDNS/Bonjour.

### Network

* DNS packet parsing.
* Service Discovery.
* 232 Tests.

## 3.28.0 - 2026-11-22

USB HID.

### Platform

* HID-Enumeration.
* Raw Reports.
* 229 Tests.

## 3.27.0 - 2026-11-22

WLAN.

### Platform

* Interface-Enumeration.
* Netzwerk-Scan.
* 227 Tests.

## 3.26.0 - 2026-11-22

Bluetooth.

### Platform

* Radio-Enumeration.
* Device-Enumeration.
* 225 Tests.

## 3.25.0 - 2026-11-22

Display-Schnittstellen.

### Platform

* Monitor-Enumeration.
* Fullscreen/Window-Placement.
* Work-Area.
* 223 Tests.

## 3.24.0 - 2026-11-22

Hardware-Schnittstellen.

### IO

* Serial/UART.
* COBS/Length/Delimiter-Framing.
* TCP/UDP.
* Modbus TCP.
* 221 Tests.

## 3.23.0 - 2026-11-22

Layout-/Accessibility-Fix.

### Fix

* `window.layout.add` synchronisiert Root-Baum.
* Widgets werden gezeichnet und sind in der Accessibility-Struktur.
* 216 Tests.

## 3.22.0 - 2026-11-22

Tray.

### Platform

* `TrayIcon`.
* Menue.
* 214 Tests.

## 3.21.0 - 2026-11-22

Picker-Widgets.

### UI

* `ColorPicker`.
* `FilePicker`.
* 213 Tests.

## 3.20.0 - 2026-11-22

Formular-Validierung.

### App

* `Form`/`Field`.
* Validatoren.
* 211 Tests.

## 3.19.0 - 2026-11-22

Widget-Integration.

### UI

* RadioButton/SpinBox/ListBox im Designer.
* Dieselben Typen als LLM-Tools.
* 208 Tests.

## 3.18.0 - 2026-11-22

Accessibility-Audit.

### Accessibility

* Rollen fuer neue Widgets.
* `tools/a11y_audit.py`.
* Screenreader-Checkliste.
* 208 Tests.

## 3.17.0 - 2026-11-22

Weitere Widgets.

### UI

* `RadioButton`.
* `SpinBox`.
* `ListBox`.
* 206 Tests.

## 3.16.0 - 2026-11-22

ttk-Widgets.

### Compat

* `ttk.Notebook`.
* `ttk.Treeview`.
* `ttk.Progressbar`.
* `ttk.Combobox`.
* 203 Tests.

## 3.15.0 - 2026-11-22

MCP.

### AI

* `MCPClient`.
* `MCPServer`.
* stdio JSON-RPC.
* 201 Tests.

## 3.14.0 - 2026-11-22

Vision.

### AI

* Bild-Helfer.
* Ollama `images`.
* OpenAI `image_url`.
* Agent `image`.
* 199 Tests.

## 3.13.0 - 2026-11-22

Qt-Compat.

### Compat

* `amfwx.compat.qt`.
* QApplication/QMainWindow/Layouts/Controls.
* 197 Tests.

## 3.12.0 - 2026-11-22

JUCE-Compat.

### Compat

* `amfwx.compat.juce`.
* Window/Controls.
* 195 Tests.

## 3.11.0 - 2026-11-22

GTK-Compat.

### Compat

* `amfwx.compat.gtk`.
* Box/Grid/Controls.
* 193 Tests.

## 3.10.0 - 2026-11-22

wxWidgets-Compat.

### Compat

* `amfwx.compat.wx`.
* Frame/Panel/Sizer/Controls.
* 191 Tests.

## 3.9.0 - 2026-11-22

Tkinter-Compat.

### Compat

* `amfwx.compat.tkinter`.
* Tk/Frame/Label/Button/Entry/Checkbutton.
* Variablen.
* pack/grid/place.
* 189 Tests.

## 3.8.0 - 2026-11-22

Designer-Resize/Undo.

### UI

* Resize-Handle.
* Undo/Redo.
* 186 Tests.

## 3.7.0 - 2026-11-22

RichText.

### UI

* `RichDocument`.
* `RichText`.
* HTML-Subset.
* 184 Tests.

## 3.6.0 - 2026-11-22

Studio/Projektstarter.

### Platform

* `Studio`.
* Templates.
* Scaffolding.
* 182 Tests.

## 3.5.0 - 2026-11-22

DB/Netzwerk.

### Platform

* `Database`.
* `HttpClient`.
* 179 Tests.

## 3.4.0 - 2026-11-22

Quick/State vollstaendig.

### UI

* `Stack`/`VStack`/`HStack`.
* `ForEach`.
* `ListState`.
* 176 Tests.

## 3.3.0 - 2026-11-22

Designer.

### UI

* `DesignerDocument`.
* `DesignerCanvas`.
* `DesignerWindow`.
* JSON und Codegen.
* 174 Tests.

## 3.2.0 - 2026-11-22

PDF/Bridge-Tests.

### UI/PDF

* `Canvas.save_pdf`.
* `Window.render_to_pdf`.
* AMFW-Bridge-Tests.
* 171 Tests.

## 3.1.0 - 2026-11-22

AI-/SDK-Haertung.

### AI/SDK

* Streaming fuer Ollama/OpenAI-kompatibel.
* Retry/Backoff.
* Conversation-Persistenz.
* DPAPI-KeyStore.
* Ollama pull/delete.
* ProgressBar-Tool.
* 167 Tests.

## 3.0.0 - 2026-11-22

SDK + LLM-Integration.

### SDK

* `create_sdk`/`SDK`.
* `UiSession` mit LLM-Tools.
* Ollama-Provider.
* OpenAI-kompatible Provider.
* `LLMAgent` Tool-Loop.
* Bridges im SDK.
* 162 Tests.

## 2.5.2 - 2026-11-22

Security-Helfer.

### Security

* `verify_native_dlls`.
* `safe_resource_name`.
* ZIP-Path-Traversal-Schutz.
* 156 Tests.

## 2.5.1 - 2026-11-22

Security-Haertung.

### Security

* SHA-256-Manifest fuer native DLLs.
* `tools/verify_native.py`.
* Audit-Doku.
* 153 Tests.

## 2.5.1 - 2026-11-22

SignPath-Foundation-Integration.

### Distribution

* GitHub-Actions-Workflow.
* Artefakt-Konfiguration.
* Antrags-Doku.
* 152 Tests.

## 2.5.0 - 2026-11-22

Mixer-Preset-Datei (JSON).

### Audio

* `save_file`.
* `load_file`.
* 152 Tests.

## 2.4.2 - 2026-11-22

Mixer-Preset-Datei.

### Audio

* `save_presets`.
* `load_presets`.
* Settings-Anbindung.
* 152 Tests.

## 2.4.1 - 2026-11-22

Mixer-Presets.

### Audio

* `MixerPanel.state`.
* `apply_state`.
* 151 Tests.

## 2.4.0 - 2026-11-22

Mixer-UI.

### Audio

* `MixerStrip`.
* `MixerPanel`.
* Slider/Gain-Kopplung.
* 151 Tests.

## 2.3.1 - 2026-11-22

Plugin-Beispiel.

### Platform

* `examples/plugins/hello.py`.
* Lade-Test.
* 150 Tests.

## 2.3.0 - 2026-11-22

Plugin-Registry.

### Platform

* `Plugin`.
* `PluginRegistry`.
* Modul-Laden.
* 149 Tests.

## 2.2.2 - 2026-11-22

Skalierte Snapshots.

### UI

* `render_to_png(..., scale=...)`.
* 2x-Snapshot.
* 148 Tests.

## 2.2.1 - 2026-11-22

DSP-Graph.

### Audio

* `DspGraph`.
* Effektkette.
* 147 Tests.

## 2.2.0 - 2026-11-22

DSP-Basis.

### Audio

* `AudioBuffer`.
* `Gain`.
* `Mixer`.
* `Biquad`.
* 146 Tests.

## 2.1.1 - 2026-11-22

Media-/Shader-Fuzzing.

### Haertung

* AVI-Fuzz.
* WAV-Fuzz.
* Shader-Fuzz.
* 144 Tests.

## 2.1.0 - 2026-11-22

Visuelle Regression.

### Haertung

* Snapshot fuer Dark.
* Snapshot fuer Light.
* Snapshot fuer High Contrast.
* 142 Tests.

## 2.0.3 - 2026-11-22

Asset-Fuzzing.

### Haertung

* PNG-Fuzz.
* WebP-Fuzz.
* TrueType-Fuzz.
* 142 Tests.

## 2.0.2 - 2026-11-22

Parser-Fuzzing.

### Haertung

* MIDI-Fuzz.
* MP4-Fuzz.
* ResourcePack-Fehler.
* 140 Tests.

## 2.0.1 - 2026-11-22

Fehlerinjektion: fehlende UIA-DLL.

### Haertung

* Fenster funktioniert ohne native UIA-DLL.
* MSAA-Fallback bleibt.
* 138 Tests.

## 2.0.0 - 2026-11-22

AMFWX 2.0: Resources und Crash-Logging.

### Plattform

* `ResourcePack` (ZIP).
* Theme/i18n/Icons aus Ressourcen.
* `CrashLogger`.
* Rotating Crash-Log.
* 137 Tests.

## 1.9.0 - 2026-11-22

MIDI-Parser.

### Audio

* `MidiFile`.
* `MidiNote`.
* SMF-Header/Tracks.
* Tempo/Division.
* `MidiPlayer` (winmm).
* 134 Tests.

## 1.8.0 - 2026-11-22

Animation/Timeline.

### UI

* `Animation`.
* `Timeline`.
* `AnimatedValue`.
* Easing-Funktionen.
* 132 Tests.

## 1.7.0 - 2026-11-22

Deklarative QuickView-Schicht.

### UI

* `State`.
* `QuickView`.
* Rebuild bei State-Aenderung.
* `Text`/`TextField`.
* 130 Tests.

## 1.6.0 - 2026-11-22

Model-Schicht.

### Daten

* `ListModel`.
* `TableModel`.
* `SortFilterModel`.
* Change-Callbacks.
* 128 Tests.

## 1.5.4 - 2026-11-22

Frame-Drop/Duplicate.

### Video/Audio

* Zaehler fuer dekodierte Frames.
* Drop bei Rueckstand.
* Duplicate bei Vorlauf.
* 126 Tests.

## 1.5.3 - 2026-11-22

Audio-Clock nach Seek.

### Video/Audio

* `audio_offset`.
* Audio-Position + Offset als Master.
* 126 Tests.

## 1.5.2 - 2026-11-22

MediaPlayer-Audio-Seek.

### Video/Audio

* Audio-Buffer beim Seek neu angesetzt.
* AudioPlayer neu gestartet.
* 126 Tests.

## 1.5.1 - 2026-11-22

UIA-Namensereignisse.

### Accessibility

* Bridge meldet Namensaenderungen.
* `notify_name` bei Sync.
* 126 Tests.

## 1.5.0 - 2026-11-22

Audio-Seek.

### Audio

* `mf_audio_seek`.
* `MediaAudioStream.seek`.
* 126 Tests.

## 1.4.1 - 2026-11-22

UIA-Ereignisse.

### Accessibility

* `notify_structure`.
* `notify_name`.
* `UiaRaiseStructureChangedEvent`.
* `UiaRaiseAutomationPropertyChangedEvent`.
* 125 Tests.

## 1.4.0 - 2026-11-22

Audio-Queue.

### Audio

* `AudioQueuePlayer`.
* PCM-Chunks an waveOut.
* `MediaAudioStream.play`.
* 125 Tests.

## 1.3.2 - 2026-11-22

UIA-Fokusereignisse.

### Accessibility

* `amfwx_uia_notify_focus`.
* `UiaRaiseAutomationEvent`.
* Fokuswechsel an Screenreader.
* 124 Tests.

## 1.3.1 - 2026-11-22

UIA-Bounds.

### Accessibility

* `IRawElementProviderFragment`.
* echte Widget-Bounds.
* Screen-Koordinaten.
* 124 Tests.

## 1.3.0 - 2026-11-22

Native UIA-Patterns.

### Accessibility

* InvokePattern.
* TogglePattern.
* ValuePattern.
* Label-Name.
* AutomationId.

### Accessibility

* `uia_provider.dll` (MinGW, statisch).
* `IRawElementProviderSimple`.
* Invoke/Value/Toggle.
* UIA erkennt Button.
* `AutomationId`.
* 124 Tests.

## 1.2.1 - 2026-11-21

Provider-Bridge.

### Accessibility

* `AccessibilityBridge`.
* Tree -> Proxy-Namen.
* Tree -> Checkbox-State.
* Proxy-Fokus -> Widget-Fokus.
* 123 Tests.

## 1.2.0 - 2026-11-21

Accessibility-Provider-Architektur.

### Accessibility

* `AccessibilityTree`.
* `AccessibilityNode`.
* Rollen.
* Label-Zuordnung.
* Werte/Zustaende.
* Aktionen.
* 122 Tests.

## 1.1.3 - 2026-11-21

Tab-Navigation.

### Accessibility

* `WS_TABSTOP` fuer Button/Edit-Proxies.
* `IsDialogMessage` im Loop.
* Tab wechselt zwischen Proxies.
* 120 Tests.

## 1.1.2 - 2026-11-21

Uninstaller-Fix.

### Installer

* Registry wird vor rmdir geloescht.
* Shortcuts werden vor rmdir geloescht.
* Deinstallation entfernt Zielverzeichnis, Registry und Links.
* 119 Tests.

## 1.1.1 - 2026-11-21

NVDA-Test bestanden.

### Accessibility

* NVDA 2026.3.1 erkennt Fenstertitel.
* Button: "Aktion, Schalter".
* Edit: "Eingabefeld, Textfeld".
* MSAA-Pfad mit echtem Screenreader bestaetigt.
* 119 Tests.

## 1.1.0 - 2026-11-21

Audio-Streaming.

### Audio

* `mf_audio_open/next/close`.
* `MediaAudioStream`.
* PCM-Chunks.
* 119 Tests.

## 1.0.9 - 2026-11-21

MSAA-Bounds.

### Accessibility

* `read_location`.
* `get_accLocation`.
* Proxy-Bounds 1x1.
* 118 Tests.

## 1.0.8 - 2026-11-21

MSAA-Selection.

### Accessibility

* `read_selection`.
* `get_accSelection`.
* 117 Tests.

## 1.0.7 - 2026-11-21

MSAA-Fokus lesen.

### Accessibility

* `read_focus`.
* `get_accFocus`.
* `SetFocus` nach `accSelect`.
* 116 Tests.

## 1.0.6 - 2026-11-21

MSAA-Fokus.

### Accessibility

* `select_accessible`.
* `accSelect`.
* Fokus auf Proxy.
* 115 Tests.

## 1.0.5 - 2026-11-21

MSAA Value setzen.

### Accessibility

* `set_accessible_value`.
* `put_accValue`.
* Edit-Text ueber MSAA.
* 114 Tests.

## 1.0.4 - 2026-11-21

MSAA State/Value.

### Accessibility

* `get_accValue`.
* `get_accState`.
* CheckBox role 44.
* Edit value.
* 113 Tests.

## 1.0.3 - 2026-11-21

MSAA-DefaultAction.

### Accessibility

* `do_default_action`.
* Screenreader-Aktion ueber MSAA.
* Button-Callback.
* 112 Tests.

## 1.0.2 - 2026-11-21

MSAA-Fallback.

### Accessibility

* `read_accessible`.
* native Proxies liefern MSAA-Rollen.
* Button: role 43.
* Name/Edit-Rolle.
* 111 Tests.

## 1.0.1 â€“ 2026-11-21

Seek in MediaStream/MediaPlayer.

### Video

* `mf_seek`.
* `MediaStream.seek`.
* `MediaPlayer.seek`.
* 110 Tests.

## 1.0.0 â€“ 2026-11-21

AMFWX 1.0.

### Kern

* 109 Tests.
* Accessibility-Proxies mit Aktionen.
* H.264/MP4 + Audio.
* GPU-Compute D3D12.
* Docking.
* Installer/Signatur.

### Bekannte Grenzen

* keine oeffentliche CA.
* keine vollstaendige Screenreader-Zertifizierung.
* keine 100%-UIA-Pattern auf Proxies.

## 0.99.0 â€“ 2026-11-21

Proxy-Aktionen.

### UIA/MSAA

* native Button-Klicks -> AMFWX.
* CheckBox-Toggle.
* Edit-Text -> Widget.
* `_proxy_command`.
* BM_SETCHECK/BTN_CLICK.
* 109 Tests.

## 0.98.0 â€“ 2026-11-21

Native Accessibility-Proxies.

### UIA/MSAA

* 1Ã—1 STATIC/BUTTON/EDIT pro Widget.
* UIA sieht Namen und Rollen.
* `sync_accessibility`.
* dynamische Aktualisierung ueber invalidate.
* UIA-Client: Text/Button/Edit sichtbar.
* 108 Tests.

## 0.97.0 â€“ 2026-11-21

Audio-Clock-Sync.

### Video/Audio

* Audio-Position als Master.
* Videoframes folgen der Audiozeit.
* Frame-Begrenzung pro Advance.
* 107 Tests.

## 0.96.0 â€“ 2026-11-21

Audio-Position.

### Audio

* `waveOutGetPosition`.
* `AudioPlayer.position()`.
* Grundlage fuer Audio-Clock-Sync.
* 107 Tests.

## 0.95.0 â€“ 2026-11-21

Dock-Presets projektweit.

### UI

* `save_presets`.
* `load_presets`.
* Settings-Anbindung.
* 107 Tests.

## 0.94.0 - 2026-11-21

Dock-Layout-Presets.

### UI

* `save_layout`.
* `apply_layout`.
* benannte Layouts.
* 106 Tests.

## 0.93.0 â€“ 2026-11-21

Floating-Pane wieder andocken.

### UI

* `Window.on_close`.
* `DockManager.redock`.
* Widget-Reparenting.
* 105 Tests.

## 0.92.0 â€“ 2026-11-21

Dock-Floating.

### UI

* `DockManager.float_pane`.
* Pane als eigenes Fenster.
* Widget-Reparenting.
* Layout-Neuberechnung.
* 105 Tests.

## 0.91.0 â€“ 2026-11-21

Dock-Persistenz.

### UI

* `DockManager.state()`.
* `save_state`/`load_state`.
* Bereiche/GrÃ¶ÃŸen/aktive Tabs.
* Settings-Anbindung.
* 104 Tests.

## 0.90.0 â€“ 2026-11-21

Dock-Tabs.

### UI

* mehrere Widgets pro DockPane.
* Tab-Leiste.
* aktiver Tab.
* Tab-Klick.
* 103 Tests.

## 0.89.0 â€“ 2026-11-21

Dock-Panes resizable.

### UI

* Divider-Erkennung.
* links/rechts/unten.
* Drag-Resize.
* MindestgrÃ¶ÃŸen.
* 102 Tests.

## 0.88.0 â€“ 2026-11-21

Dock-Titelzeile.

### UI

* Panes mit 24-px-Titelzeile.
* Inhalte unter dem Titel.
* zentrale FlÃ¤che korrekt.
* 101 Tests.

## 0.87.0 â€“ 2026-11-21

Docking-Basis.

### UI

* `DockManager`.
* `DockPane`.
* links/rechts/unten.
* zentraler Bereich.
* Layout + Paint.
* 101 Tests.

## 0.86.0 â€“ 2026-11-21

Synchronisierter MediaPlayer.

### Video/Audio

* `MediaPlayer`.
* Video-Stream + optionale Audio-Spur.
* Play/Pause/Close.
* `advance`.
* Zeitbasis.
* 100 Tests.

## 0.85.0 â€“ 2026-11-21

MP4-Audio Ã¼ber Media Foundation.

### Audio

* `mf_audio_decode`.
* PCM-Ausgabe.
* `MediaAudio`.
* WAV-Konvertierung.
* `AudioPlayer`-Anbindung.
* 99 Tests.

## 0.84.0 â€“ 2026-11-21

VideoView mit MediaStream.

### Video

* `MediaVideo.stream()`.
* `VideoView` nutzt sequenziellen Stream.
* echter H.264-Frame im Widget.
* `close`.
* 98 Tests.

## 0.83.0 â€“ 2026-11-21

Sequenzieller H.264-Stream.

### Video

* `mf_open`/`mf_next`/`mf_close`.
* persistenter MF-Reader.
* `MediaStream`.
* sequenzielle Frames.
* 98 Tests.

## 0.82.0 â€“ 2026-11-21

MediaVideo im VideoView.

### Video

* `VideoView` akzeptiert `MediaVideo`.
* Erster H.264-Frame im Widget.
* `VideoPlayer` unterstÃ¼tzt Integer-Framecounts.
* 97 Tests.

## 0.81.0 â€“ 2026-11-21

H.264/MP4 Ã¼ber Media Foundation.

### Video

* native `mfdecode.dll`.
* MF Source Reader.
* NV12-Ausgabe.
* NV12â†’BGRA.
* `MediaVideo`.
* 4K-Frame getestet.
* 96 Tests.

## 0.80.0 â€“ 2026-11-21

MP4-Container-/Track-Parser.

### Video

* ISO-BMFF-Boxen.
* ftyp/moov/mvhd.
* trak/tkhd/mdia/mdhd/hdlr.
* stsd/avc1.
* `Mp4Info`/`Mp4Track`.
* Track-Metadaten.
* 94 Tests.

## 0.79.0 â€“ 2026-11-21

GPU-Compute funktioniert.

### GPU

* SDL_GPU D3D12.
* DXIL/DXBC.
* UAV in `register(u0, space1)`.
* Storage-Buffer.
* Dispatch.
* `SDL_DownloadFromGPUBuffer`.
* Readback.
* Ergebnis `(1,0,0,1)`.
* 93 Tests.

## 0.78.0 - 2026-11-21

GPU-Compute-Versuch.

### GPU

* amfwx/gpu.py.
* DXBC/DXIL-Compile.
* SDL_GPU D3D12-Geraet.
* Pipeline-Erzeugung schlaegt mit E_INVALIDARG fehl.
* C-Struktur-Probe bestaetigt ABI-Layout.

### Tests

* 92 Tests.

## 0.77.0 â€“ 2026-11-21

HLSLâ†’DXBC-Shader-Compiler.

### Shader

* `d3dcompiler_47` per ctypes.
* `compile_hlsl`.
* Compute-Shader getestet.
* DXBC-Blob.
* Fehlerdiagnose.
* 92 Tests.

## 0.76.0 â€“ 2026-11-21

SDL3-Hardware-Backend-Info.

### SDL3

* `SDL_GetCurrentVideoDriver`.
* `SDL_GetRendererName`.
* `backend_info()`.
* D3D11-Hardware-Backend erkannt.
* Dummy/Software-Test.
* 90 Tests.

## 0.75.0 â€“ 2026-11-21

VideoView.

### Video

* `VideoView`.
* Play/Pause.
* `advance`.
* Frame-Cache/Skalierung.
* Space-Taste.
* 89 Tests.

## 0.74.0 â€“ 2026-11-21

AVI/MJPEG-Video.

### Video

* AVI-RIFF-Parser.
* avih/strh/strf.
* movi/JPEG-Frames.
* `AviVideo`.
* `VideoPlayer`.
* Frame Ã¼ber JPEG-Decoder.
* 88 Tests.

## 0.73.0 â€“ 2026-11-21

TreeView-Drag-and-Drop.

### TreeView

* Drag-Schwelle.
* Reparenting.
* Zyklus-Schutz.
* `on_move`.
* 87 Tests.

## 0.72.0 â€“ 2026-11-21

TableView-Multi-Select.

### TableView

* `multi_select`.
* `selected_rows`.
* Toggle-Auswahl.
* `on_select_many`.
* 86 Tests.

## 0.71.0 â€“ 2026-11-21

Software-Shader.

### Grafik

* Vertex-/Fragment-Shader.
* Varying-Interpolation.
* Z-Buffer.
* perspektivische Interpolation.
* `ShaderRenderer`.

### Tests

* 85 Tests.

## 0.70.0 â€“ 2026-11-21

UI-Screenshot-Baseline.

### Tests

* deterministischer Snapshot.
* SHA-256-Baseline.
* `tools/ui_snapshot.py`.
* `Window.render_to_png`.
* 84 Tests.

## 0.69.0 â€“ 2026-11-21

Widget-Fuzzing.

### Tests

* deterministischer Random-Input.
* TextEdit/TableView/TreeView/Tabs/PropertyGrid.
* 400 Iterationen.
* 83 Tests.

## 0.68.0 â€“ 2026-11-21

WAV-Audio.

### Audio

* WAV-Parser.
* PCM/IEEE-Float.
* `AudioPlayer` Ã¼ber `waveOut`.
* Play/Stop.
* Keine externen DLLs.

### Tests

* 82 Tests.

## 0.67.0 â€“ 2026-11-21

TreeView-Komfort.

### TreeView

* optionale Icons.
* Tastatur Expand/Collapse.
* `expand_all`/`collapse_all`.
* Icon-Farben/Text.

### Tests

* 82 Tests.

## 0.66.0 â€“ 2026-11-21

SDL3-Eventloop.

### SDL3

* `Sdl3Loop`.
* Frame-Callback.
* Present pro Frame.
* Event-Poll/Quit.
* Dummy-Test.

### Tests

* 81 Tests.

## 0.65.0 â€“ 2026-11-21

MSAA/IAccessible-Bridge.

### MSAA

* `Accessible` mit IDispatch+IAccessible-Vtable.
* virtuelles Kindmodell.
* `accName`, `accRole`, `accState`, `accLocation`, `accHitTest`, `accNavigate`.
* `LresultFromObject` fÃ¼r `OBJID_CLIENT`.
* `Window.enable_msaa`.
* Direkter Kind-/Namens-Test.
* Externer MSAA-Client sieht weiterhin 0 Kinder.

### Tests

* 80 Tests.

## 0.64.0 â€“ 2026-11-21

UIA-Callbacks auf UI-Thread.

### COM

* `Window.invoke`.
* `WM_APP_INVOKE`.
* UIA-Callbacks werden per `SendMessage` marshallt.
* Test aus Worker-Thread.

### Tests

* 79 Tests.

## 0.63.0 â€“ 2026-11-21

WebP Ã¼ber libwebp.

### WebP

* libwebp 1.5.0 aus Quelltext mit MSVC gebaut.
* `libwebp.dll`/`libsharpyuv.dll`.
* `decode_webp`.
* `encode_webp`.
* `Canvas.from_webp`.
* `probe_webp`.

### Eigener Installer

* `AMFWX-Own-Setup-0.63.0.exe`.
* AMFWX-GUI, Payload-ZIP, Shortcuts, Uninstaller.
* Silent-Modus `/S /D=`.
* Registry-Uninstall-Eintrag.

### Tests

* 78 Tests.

## 0.62.0 â€“ 2026-11-21

SDL3-Renderer.

### SDL3

* Fenster via `SDL_CreateWindow`.
* Renderer via `SDL_CreateRenderer`.
* Streaming-Textur BGRA8888.
* `SDL_UpdateTexture`.
* `SDL_RenderTexture`/`SDL_RenderPresent`.
* `SDL_PollEvent`.
* `Sdl3Renderer`.

### Tests

* 77 Tests.

## 0.61.0 â€“ 2026-11-21

SDL3 aus Quelltext gebaut.

### SDL3

* Visual Studio 2022 Build Tools gefunden.
* SDL3 3.4.20 aus offiziellem Quelltext gebaut.
* `SDL3.dll` als Vendor-Binary.
* `probe_sdl3()` erkennt Window/Events/Audio/Gamepad/GPU.
* Renderer noch nicht implementiert.

### Tests

* 76 Tests.

## 0.60.0 â€“ 2026-11-21

COM-Thread-Isolation und Blocker-Dokumentation.

### UIA

* `RLock` in Provider/TextProvider/TextRange.
* Callback-Serialisierung.
* Dokumentation der offenen Hosting-/Tooling-Punkte.

### Tests

* 76 Tests.

## 0.59.0 â€“ 2026-11-21

Splitter.

### Widgets

* `Splitter` horizontal/vertikal.
* Divider-Drag.
* Ratio-Persistenz.
* `on_change`.

### Tests

* 76 Tests.

## 0.58.0 â€“ 2026-11-21

StatusBar und ToolBar.

### Widgets

* `StatusBar` mit Feldern.
* `ToolBar` mit Aktionen.
* Hover/Pressed-ZustÃ¤nde.
* Trennlinien.

### Tests

* 75 Tests.

## 0.57.0 â€“ 2026-11-21

UntermenÃ¼s.

### MenÃ¼s

* `Menu.add_menu`.
* verschachtelte `MenuPopup`.
* UntermenÃ¼-Indikator.
* Ã–ffnen rechts neben dem Eintrag.
* Aktionen in UntermenÃ¼s.

### Tests

* 74 Tests.

## 0.56.0 â€“ 2026-11-21

ImageView.

### Widgets

* `ImageView`.
* Fit-Modus.
* Zoom per Wheel.
* Pan per Drag.
* bilineare Skalierung.
* `Canvas.draw_image_xy`.

### Tests

* 73 Tests.

## 0.55.0 â€“ 2026-11-21

Recent-Files-MenÃ¼.

### Editor

* â€žZuletztâ€œ-MenÃ¼.
* dynamische EintrÃ¤ge aus Settings.
* Ã–ffnen per Klick.
* Aktualisierung nach Laden/Speichern.
* leerer Zustand.

### Tests

* 72 Tests.

## 0.54.0 â€“ 2026-11-21

Fenstergeometrie-Persistenz.

### App

* `Window.geometry`.
* `restore_geometry`.
* `save_geometry`/`load_geometry`.
* Editor speichert Geometrie beim SchlieÃŸen.
* Wiederherstellung aus Settings.

### Tests

* 72 Tests.

## 0.53.0 â€“ 2026-11-21

Settings und Recent Files.

### App

* `Settings` JSON-Store.
* atomisches Speichern.
* Recent-Files-Liste.
* Editor schreibt Recent-Files.
* `default_path` unter `%APPDATA%`.

### Tests

* 71 Tests.

## 0.52.0 â€“ 2026-11-21

Canvas-Bildoperationen.

### Canvas

* `scaled` bilinear/nearest.
* `crop`.
* `thumbnail`.
* unabhÃ¤ngige RÃ¼ckgabe-Canvas.

### Tests

* 70 Tests.

## 0.51.0 â€“ 2026-11-21

FontDialog.

### UI

* Fontauswahl aus Windows-Fonts.
* GrÃ¶ÃŸenfeld.
* Live-Vorschau.
* `FontDialog.pick`.
* TTF-Laden in der Vorschau.

### Tests

* 69 Tests.

## 0.50.0 â€“ 2026-11-21

ColorDialog.

### UI

* RGB-Eingabefelder.
* Farbvorschau.
* `ColorDialog.pick`.
* `ColorSwatch`.
* Clamping 0â€“255.

### Tests

* 68 Tests.

## 0.49.0 â€“ 2026-11-21

Suchen/Ersetzen.

### Text

* `TextEdit.find`.
* `find_next`.
* `replace_all`.
* `select_range`.
* `FindReplaceDialog`.
* Editor-MenÃ¼ â€žSuchen/Ersetzenâ€œ.

### Tests

* 67 Tests.

## 0.48.0 â€“ 2026-11-21

Bild-Clipboard (CF_DIB).

### Clipboard

* `set_image`.
* `get_image`.
* `Canvas.from_clipboard_image`.
* 24/32-bit DIB.
* Bottom-up-Zeilen.
* BGRA-Konvertierung.

### Tests

* 66 Tests.

## 0.47.0 â€“ 2026-11-21

TableView-Sortierung und Spaltenbreiten.

### UI

* Sortierung per Header-Klick.
* Auf-/absteigend.
* Sort-Indikator.
* Spaltenbreiten per Drag.
* Doppelte Mouse-Handler bereinigt.

### Tests

* 65 Tests.

## 0.46.0 â€“ 2026-11-21

IUIAutomation-Client-Test korrigiert.

### UIA

* `ElementFromHandle` mit vollstÃ¤ndigem HWND erfolgreich.
* Client sieht Window + native TitleBar.
* Kein `WM_GETOBJECT` an das Python-Fenster.
* Custom-Provider wird nicht aufgerufen.

### Tests

* 64 Tests.

## 0.45.0 â€“ 2026-11-21

KontextmenÃ¼s.

### UI

* `Widget.context_menu`.
* Rechtsklick-Handling.
* `ContextMenu`-Overlay.
* Aktionen mit Shortcut-Anzeige.
* Vererbung zum Eltern-Widget.

### Tests

* 64 Tests.

## 0.44.0 â€“ 2026-11-21

UIA TransformPattern.

### UIA

* `ITransformProvider`.
* `Move`.
* `Resize`.
* `CanMove`.
* `CanResize`.
* `CanRotate`.
* Fenster-Root.

### Tests

* 63 Tests.

## 0.43.0 â€“ 2026-11-21

UIA-COM-Regressionstests.

### UIA

* `GUID.__str__` getestet.
* QI fÃ¼r Simple/Fragment/Root getestet.
* Simple-Vtable: Host/Pattern/Property getestet.
* COM-Initialisierung in `enable_uia`.
* Externer UIA-Client weiterhin ohne Kinder.

### Tests

* 62 Tests.

## 0.42.0 â€“ 2026-11-21

UIA-Simple-Vtable korrigiert.

### UIA

* `get_HostRawElementProvider`, `GetPatternProvider` und `GetPropertyValue`
  waren in der Vtable vertauscht.
* Reihenfolge jetzt:
  1. ProviderOptions
  2. HostRawElementProvider
  3. GetPatternProvider
  4. GetPropertyValue
* Externer UIA-Client-Test bleibt ohne Kinder, aber Interface-Layout ist korrekt.

### Tests

* 60 Tests.

## 0.41.0 â€“ 2026-11-21

GUID-/QueryInterface-Fix im UIA-Provider.

### UIA

* `GUID.__str__` implementiert.
* QueryInterface verglich vorher Objekt-ReprÃ¤sentationen statt IIDs.
* Simple/Fragment/Root QI liefern jetzt S_OK.
* Externer UIA-Client-Test bleibt trotzdem ohne Kinder.

### Tests

* 60 Tests.

## 0.40.0 â€“ 2026-11-21

UIA-Client-Test und Navigationskorrekturen.

### UIA

* `WM_GETOBJECT`-Parameter durchgereicht.
* `NavigateDirection` korrigiert.
* IsControlElement/IsContentElement.
* Host-RawElementProvider reaktiviert.
* Externer Test mit UIAutomationClient durchgefÃ¼hrt.

### Testergebnis

* Fenster wird erkannt.
* Kinder werden nicht erkannt.
* Provider fÃ¤llt auf nativen Host zurÃ¼ck.
* Nicht screenreader-produktionsreif.

### Tests

* 60 Tests.

## 0.39.0 â€“ 2026-11-21

Normal-Mapping.

### 3D

* Normal-Map-Parameter.
* Face-Tangente/Bitangente.
* Normal-Map-Sampling.
* Beleuchtung mit gestÃ¶rter Normale.

### Tests

* 60 Tests.

## 0.38.0 â€“ 2026-11-21

UIA Grid-/TablePattern.

### UIA

* `IGridProvider`.
* `ITableProvider`.
* Zell-Provider.
* `GetItem`.
* Row/ColumnCount.
* RowOrColumnMajor.

### Tests

* 59 Tests.

## 0.37.0 â€“ 2026-11-21

GPOS Mark-to-Ligature.

### Font

* MarkToLigature-Parser.
* LigatureArray/LigatureAttach.
* Komponenten-Anker.
* `mark_ligature_positions`.
* `positioned()` nutzt Ligatur-Anker vor Basis-Ankern.

### Tests

* 58 Tests.

## 0.36.0 â€“ 2026-11-21

GPOS Mark-to-Mark.

### Font

* MarkToMark-Parser.
* Mark1Array/Mark2Array.
* Mark-Klassen.
* `mark_mark_positions`.
* `positioned()` verkettet Marken.

### Grenzen

* kein Mark-to-Ligature
* keine Device-Tables
* keine Variation-Anchors

### Tests

* 58 Tests.

## 0.35.0 â€“ 2026-11-21

Mipmaps und bilineare Texturfilterung.

### 3D

* Mipmap-Kette.
* trilineare LOD-Auswahl.
* bilineare Abtastung.
* LOD aus DreiecksflÃ¤che/TexturgrÃ¶ÃŸe.

### Tests

* 58 Tests.

## 0.34.0 â€“ 2026-11-21

Perspektivisch korrekte Texturen.

### 3D

* 1/w pro Vertex.
* perspektivische UV-Interpolation.
* keine affine Verzerrung mehr.
* Z-Buffer unverÃ¤ndert.

### Tests

* 56 Tests.

## 0.33.0 â€“ 2026-11-21

GPOS Mark-to-Base.

### Font

* MarkArray/BaseArray.
* Anchor Format 1â€“3.
* Mark-Klassen.
* `positioned()`.
* Mark-Offsets im Rasterizer.

### Grenzen

* kein Mark-to-Mark
* kein Mark-to-Ligature
* keine Device-Tables
* keine RTL-spezifische Mark-Kette

### Tests

* 56 Tests.

## 0.32.0 â€“ 2026-11-21

PyInstaller-Build und Authenticode-Testsignatur.

### Distribution

* `dist\AMFWX\AMFWX.exe` mit PyInstaller 6.11.1 gebaut.
* `tools/sign_selfsigned.ps1`.
* Selbstsigniertes Testzertifikat.
* SHA-256-Authenticode-Signatur.
* Status `UnknownError` wegen nicht vertrauenswÃ¼rdiger Testwurzel.
* Inno-Setup/signtool fehlen.

### Tests

* 56 Tests.

## 0.31.0 â€“ 2026-11-21

UIA TogglePattern.

### UIA

* `IToggleProvider`.
* `Toggle`.
* `ToggleState`.
* CheckBox.

### Tests

* 56 Tests.

## 0.30.0 â€“ 2026-11-21

UIA RangeValuePattern.

### UIA

* `IRangeValueProvider`.
* `SetValue`.
* `Value`.
* `Minimum`/`Maximum`.
* `LargeChange`/`SmallChange`.
* `IsReadOnly`.
* Slider und ScrollBar.

### Tests

* 55 Tests.

## 0.29.0 â€“ 2026-11-21

Lam-Alef-Ligaturen.

### Arabic

* Lam + Alef.
* Lam + Alef-Madda.
* Lam + Alef-Hamza oben/unten.
* isolierte/finale Ligaturform.
* Joining-Kontext vor Lam.

### Tests

* 54 Tests.

## 0.28.0 â€“ 2026-11-21

Arabisch-Joining.

### Text

* Joining-Typen.
* Isolated/Final/Initial/Medial.
* Arabische PrÃ¤sentationsformen.
* Transparente Marks.
* Integration in TextLayout/Bidi.

### Grenzen

* keine Lam-Alef-Ligaturen
* keine GPOS-Mark-Positionierung
* kein vollstÃ¤ndiges OpenType-Feature-System
* PrÃ¤sentationsformen mÃ¼ssen im Font vorhanden sein

### Tests

* 53 Tests.

## 0.27.0 â€“ 2026-11-21

Bidi-Level nach UAX#9-Basis.

### Bidi

* Bidi-Typen.
* Basisrichtung.
* W1â€“W7.
* N1/N2.
* I1/I2.
* L2-Reordering.
* `bidi_levels`.
* `amfwx.bidi`.

### Grenzen

* keine Isolate
* keine Bracket-Pairs
* kein Arabisch-Joining
* keine vollstÃ¤ndigen Unicode-Tabellen

### Tests

* 51 Tests.

## 0.26.0 â€“ 2026-11-21

UIA-TextRange-Vertiefung und StructureChanged.

### UIA

* `Move` fÃ¼r Zeichen/Wort/Zeile/Dokument.
* `FindText`.
* BoundingRectangles fÃ¼r Text-Ranges.
* `MoveEndpointByUnit`.
* `StructureChanged` bei TreeView Expand/Collapse.

### Grenzen

* kein vollstÃ¤ndiges UAX#9
* keine SelectionProvider-Row-Erweiterung
* kein Inspect-Test

### Tests

* 49 Tests.

## 0.25.0 â€“ 2026-11-21

GPOS PairPos Format 2 (Class-Kerning).

### Font

* ClassDef Format 1/2.
* PairPos Format 2.
* class1/class2-Matrizen.
* XAdvance aus Class-Records.
* `kerning()` prÃ¼ft Einzelpaare, dann Klassen.

### Grenzen

* keine Device-Tables
* keine Mark-Positionierung
* keine Contextual-Positionierung
* kein vollstÃ¤ndiges OpenType

### Tests

* 48 Tests.

## 0.24.0 â€“ 2026-11-21

Bessere Bidi-Visualisierung.

### Text

* Basisrichtungserkennung.
* RTL-Runs zeichenweise gespiegelt.
* LTR-Runs bleiben erhalten.
* RTL-Basis spiegelt die Zeile und restauriert LTR-Runs.

### Grenzen

* kein vollstÃ¤ndiges UAX#9
* keine Isolate/Bracket-Pairs
* keine Zahlen-/Neutral-AuflÃ¶sung
* kein Arabisch-Joining

### Tests

* 48 Tests.

## 0.23.0 â€“ 2026-11-21

GPOS-Pair-Kerning.

### Font

* GPOS-Parser.
* Extension-Lookups.
* PairPos Format 1.
* `ValueRecord`-XAdvance.
* `kerning()` mit GPOS-Vorrang.
* `kern`-Fallback bleibt.

### Grenzen

* kein PairPos Format 2 (Class-based)
* keine Mark-Positionierung
* keine Device-Tables
* kein Contextual Positioning

### Tests

* 48 Tests.

## 0.22.0 â€“ 2026-11-21

GSUB-Ligaturen im TTF-Shaper.

### Font

* GSUB-Parser.
* Extension-Lookups.
* Lookup-Typ 4 LigatureSubst.
* Coverage Format 1/2.
* Ligaturen Ã¼ber Wort-Runs.
* Kerning bleibt `kern`-basiert.

### Grenzen

* kein GPOS
* keine Contextual/Chaining-Substitution
* kein Arabisch-Joining
* kein vollstÃ¤ndiges OpenType

### Tests

* 48 Tests.

## 0.21.0 â€“ 2026-11-21

UIA Expand/Collapse fÃ¼r TreeView.

### UIA

* `IExpandCollapseProvider`.
* `Expand`.
* `Collapse`.
* `ExpandCollapseState`.
* TreeView-Knoten expandieren/kollabieren Ã¼ber UIA.

### Tests

* 48 Tests.

## 0.20.0 â€“ 2026-11-21

Virtuelle UIA-Knoten fÃ¼r TreeView.

### UIA

* TreeView-Knoten als Provider.
* `ControlType_TreeItem`.
* SelectionPattern liefert ausgewÃ¤hlten Knoten.
* Expand/Collapse noch nicht als UIA-Pattern.

### Tests

* 47 Tests.

## 0.19.0 â€“ 2026-11-21

Virtuelle UIA-Row-Provider.

### UIA

* TableView-Zeilen als virtuelle Provider.
* DataItem-ControlType.
* SelectionPattern liefert die ausgewÃ¤hlte Zeile.
* Row-Provider im Baum.

### Tests

* 46 Tests.

## 0.18.0 â€“ 2026-11-21

3D-Texturen und UIA SelectionPattern.

### 3D

* `Texture`.
* UV-Koordinaten pro Face.
* affine Textursammlung.
* Cube mit UVs.

### UIA

* `ISelectionProvider` fÃ¼r TableView/TreeView.
* `GetSelection` als SAFEARRAY.
* CanSelectMultiple/IsSelectionRequired.

### Tests

* 46 Tests.

## 0.17.0 â€“ 2026-11-21

UIA TextPattern/TextRange.

### UIA

* `ITextProvider`.
* `ITextRangeProvider`.
* `UIA_TextPatternId`.
* Dokument-Range.
* Selection als SAFEARRAY.
* `GetText`, `GetEnclosingElement`, `Select`.
* Range-Basis fÃ¼r TextEdit/LineEdit.

### Grenzen

* kein vollstÃ¤ndiges Range-Moving
* keine Attribut-/Find-Implementierung
* kein `ISelectionProvider`
* kein Screenreader-/Inspect-Test

### Tests

* 45 Tests.

## 0.16.0 â€“ 2026-11-21

Echte Editor-App auf AMFWX.

### Editor

* `EditorWindow`.
* Datei-MenÃ¼: Neu/Ã–ffnen/Speichern/Speichern unter/Beenden.
* Bearbeiten: Undo/Redo/Auswahl/Kopieren/EinfÃ¼gen.
* Dirty-State und Titel.
* Statuszeile mit Tooltip.
* TextEdit-Integration.

### Tests

* 44 Tests.

## 0.15.0 â€“ 2026-11-21

Eigener Baseline-JPEG-Decoder.

### JPEG

* SOI/APP/DQT/SOF0/DHT/DRI/SOS.
* Huffman-Dekodierung.
* DC-PrÃ¤diktion.
* Dequantisierung.
* separable 2D-IDCT.
* YCbCrâ†’RGB.
* `Canvas.from_jpeg`.

### Grenzen

* kein Progressive JPEG
* kein CMYK
* kein EXIF-Orientation
* kein WebP
* keine Hardware-Codecs

### Tests

* 43 Tests.

## 0.14.0 â€“ 2026-11-21

TextEdit-Auswahl, Undo/Redo und Clipboard.

### TextEdit

* Auswahlanker und Selection-Rendering.
* Shift-Pfeile/Home/End.
* Maus-Selektion.
* Ctrl+A/C/X/V.
* Ctrl+Z/Y.
* Undo-/Redo-Snapshots.
* Clipboard-Integration.
* Modifier-Routing im Fenster.

### Tests

* 42 Tests.

## 0.13.0 â€“ 2026-11-21

Tabs, Tooltips, Charts und PropertyGrid.

### Widgets

* `TabView` mit Tabwechsel.
* `Tooltip` und automatische Hover-Tooltips.
* `Chart` mit Linie/Balken, Achsen, Grid.
* `PropertyGrid` mit Inline-Editoren.
* `Property`/`Series`.

### Tests

* 41 Tests.

## 0.12.0 â€“ 2026-11-21

DPI-Livewechsel, Rich-Clipboard, Bidi-Basis und Signing-Tooling.

### DPI

* `WM_DPICHANGED`.
* DPI-/Scale-Update.
* Neulayout und Resize.
* Datei-Drop (`WM_DROPFILES`).

### Clipboard

* HTML-Clipboard.
* Dateilisten-Clipboard.
* Text/HTML/Dateien kombiniert.

### Text

* einfache Bidi-Umordnung fÃ¼r RTL-first-Zeilen.

### Distribution

* `tools/build_app.ps1`.
* `tools/installer.iss`.
* `tools/sign.ps1`.
* `tools/verify_installer.ps1`.

### Grenzen

* kein TextPattern/SelectionPattern.
* kein GSUB/GPOS.
* kein SDL3-Renderer.
* kein Authenticode ohne Zertifikat.

### Tests

* 37 Tests.

## 0.11.0 â€“ 2026-11-21

UIA ValuePattern und Events.

### UIA

* `IValueProvider` fÃ¼r LineEdit/TextEdit.
* `SetValue`, `get_Value`, `get_IsReadOnly`.
* `UIA_ValuePatternId`.
* Fokus-Event.
* Invoke-Event.
* ValueChanged-Event.
* `UiaClientsAreListening`-Guard.

### Grenzen

* kein TextPattern
* kein SelectionPattern
* keine UIA-StructureChanged-Events
* kein Inspect.exe-Test

### Tests

* 36 Tests.

## 0.10.0 â€“ 2026-11-21

Optionaler UIA-COM-Provider.

### UIA

* `IRawElementProviderSimple`
* `IRawElementProviderFragment`
* `IRawElementProviderFragmentRoot`
* `IInvokeProvider`
* `WM_GETOBJECT`/`UiaReturnRawElementProvider`
* Navigation, BoundingRectangle, Name/ControlType/Enabled
* `window.enable_uia()`

### Grenzen

* opt-in
* keine UIA-Events
* keine Patterns auÃŸer Invoke
* keine SAFEARRAY-RuntimeId
* kein Inspect-/Screenreader-Test

### Tests

* 35 Tests.

## 0.9.0 â€“ 2026-11-21

DPI-Skalierung.

### DPI

* Per-Monitor-DPI-Awareness (`SetProcessDpiAwarenessContext`).
* `GetDpiForWindow`.
* logische Widget-Koordinaten.
* physische PrÃ¤sentation per `StretchDIBits`.
* skalierte Maus-/Touch-Koordinaten.
* `Window.dpi_scale`, `Window.scaled`.

### Grenzen

* kein `WM_DPICHANGED`-Livewechsel.
* Bitmap-Text wird beim Upscale leicht weich.
* keine Multi-Monitor-Skalierung pro Fenster.

### Tests

* 34 Tests.

## 0.8.0 â€“ 2026-11-21

Textlayout, TextEdit, Clipboard, IME, DPI und editierbare Tabellen.

### Text

* `TextLayout` mit Word-Wrap.
* Fontfallback Ã¼ber mehrere Fonts.
* `TextEdit` mehrzeilig.
* Zeilen-/Cursor-Navigation.

### Eingabe

* Unicode-Clipboard.
* IME-Hooks (`WM_IME_*`, `ImmGetCompositionStringW`).
* DPI-Erkennung (`GetDpiForWindow`).

### Tabellen/BÃ¤ume

* TableView-Zelleditor.
* `begin_edit`/`commit_edit`.
* TreeView Expand/Collapse per Klick.

### Tests

* 34 Tests.

## 0.7.0 â€“ 2026-11-21

TTF-Composite/Kerning, 3D-Kamera/Clipping, UIA-Baum, SDL-Probe und
Portable-Installer.

### Font

* `kern`-Tabelle.
* Composite-Glyphen mit XY-Offsets.
* Kerning in `draw`/`measure`.
* Latin-1 Ã¼ber cmap.

### 3D

* `Camera`.
* Near-Plane-Clipping.
* weiterhin Software-Renderer.

### Accessibility

* `UiaNode`, `tree_from_window`.
* Rollen/Bounds/Enabled/Focus.
* **kein COM-Provider**.

### Backends/Distribution

* `probe_sdl3` (nur Erkennung).
* `tools/build_portable.py`, Install/Uninstall.
* `python -m amfwx`.

### Tests

* 28 Tests.

## 0.6.0 â€“ 2026-11-21

Eigene TTF-, PNG- und Software-3D-Engines.

### Font

* TrueType-Tabellenparser.
* cmap Format 4.
* loca/hmtx.
* einfache Glyphenkonturen.
* Quadratik-Flattening.
* Rasterisierung Ã¼ber den Canvas.
* Kein GSUB/GPOS/Hinting/Composite.

### Bilder

* reiner PNG-Decoder/Encoder (8-bit, non-interlaced).
* `Canvas.save_png`/`from_png`.

### 3D

* `SoftwareRenderer`.
* Z-Buffer.
* Perspektive/LookAt/Rotation.
* Cube-Mesh.
* Flat-Shading.
* keine GPU.

### Tests

* PNG-Roundtrip.
* TTF-Rendering.
* Software-3D.
* 24 Tests.

## 0.5.0 â€“ 2026-11-21

Touch, Reverse Bridge, Dateidialoge und Interop.

### Touch/Gesten

* `TouchEvent`, `GestureEvent`, `GestureRecognizer`.
* `WM_POINTER`/`GetPointerInfo`.
* Tap/Pan/Pinch/Rotate/Swipe.

### Dateidialoge

* `open_file`, `save_file` Ã¼ber comdlg32.

### Reverse Bridge

* `AmfwxWindowHost` bettet ein AMFW-Fenster als natives Child in AMFWX ein.

### Interop

* `amfwx.interop` mit `ThemeTokens`, `from_amfw`, `to_amfwx`.
* Feature-Matrix.

### Tests

* Touch/Interop/Reverse-Bridge.
* 21 Tests.

## 0.4.0 â€“ 2026-11-21

AMFW-Bridge.

### Bridge

* `AmfwxView` hostet AMFWX-Widgets in einem AMFW-Fenster.
* Ein gemeinsamer Win32-Eventloop.
* BGRA-Canvas â†’ AMFW-Image.
* Maus/Tastatur-Weiterleitung.
* Theme-Host fÃ¼r AMFWX.

### Tests

* Bridge-Test.
* 15 Tests.

## 0.3.0 â€“ 2026-11-21

Popup-, MenÃ¼-, Tabellen- und DnD-Basis.

### Controls

* echtes ComboBox-Dropdown (`ListPopup`).
* `ScrollBar` und `ScrollArea` mit Clipping.
* `MenuBar` und MenÃ¼-Popup.
* `TableView`.
* `TreeView`/`TreeItem`.
* internes `DragEvent`/`DragManager`.

### Korrekturen

* Mauskoordinaten werden jetzt global an Widgets Ã¼bergeben.
* Overlay-Hit-Testing.
* Widget-Fokus und Theme-Zugriff.

### Tests

* 14 Tests.

## 0.2.0 â€“ 2026-11-21

Benutzbare Interaktionsbasis.

### Input

* Fokusverwaltung und Tab-Navigation.
* `WM_KEYDOWN`/`WM_CHAR`.
* `LineEdit` mit Cursor, Backspace, Delete, Home/End/Pfeilen.
* `CheckBox`, `Slider`, `ComboBox`.
* `ScrollArea` mit Clipping.

### Layout/Theme

* `GridLayout`, `FormLayout`.
* Theme-System dark/light/high-contrast.
* Rounded-Rect-Anti-Aliasing.
* `Dialog`/`MessageBox`.

### Tests

* 9 Tests: Canvas, Text, Controls, Fokus, Layouts, Dialoge, Fenster.

## 0.1.0 â€“ 2026-11-21

Erste eigenstÃ¤ndige AMFWX-Basis.

### Rasterizer

* BGRA-Canvas.
* Alpha-Blending.
* Rechtecke, Linien, Polygone, Kreise, Rounded Rects.
* BMP-Export.

### UI

* eigener Widget-Baum.
* BoxLayout.
* Label.
* Button.
* eigener Win32-Eventloop.
* DIB-Presentation.

### Text

* eingebauter 5Ã—7-Bitmap-Font.
* ASCII/GroÃŸbuchstaben.

### Tests

* Canvas.
* Polygon/Alpha.
* Text/Layout.
* BMP.
* Window-Render.


