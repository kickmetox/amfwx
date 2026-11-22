# Framework review: welche Features sind für AMFW/AMFWX relevant?

AMFW und AMFWX sind **keine Ports** dieser Frameworks. Die Liste dient als
Feature-Landkarte: Was lohnt sich als eigenständige, saubere Implementierung,
was ist architektonisch nicht sinnvoll?

## Kurzfazit

Die wichtigsten noch fehlenden *Konzepte* sind:

1. **Model/View mit echten Datenmodellen** (Qt, WPF, GTK)
2. **Deklarative UI + State + Hot Reload** (Flutter, SwiftUI, Slint)
3. **Accessibility-Tree als zentrale Schicht** (AccessKit, Qt, WinUI)
4. **Animation/Composition** (WPF/WinUI, SwiftUI, Flutter)
5. **Docking/PropertyGrid/Charts** in AMFWX (Qt, wxAUI, JUCE)
6. **Audio/MIDI** (JUCE)
7. **Plugin-/Resource-System** (Qt, JUCE, Electron)
8. **Visuelle Regression + Fuzzing** (Flutter, Qt, ImGui)
9. **Internationalisierung/RTL** (Qt, GTK, Flutter)

Nicht sinnvoll für AMFW/AMFWX:

- Electron-Node-Runtime
- komplette Webview-Engine
- Cross-Platform-Cocoa/GTK-Backends im Kern
- VST3/AU/AAX-Zertifizierung
- JavaScript-Engine
- vollständige CSS-Engine

## Feature-Matrix nach Framework

| Framework | Relevante Features | Für AMFW/AMFWX sinnvoll? |
|---|---|---|
| **Qt** | Model/View, QML, Signals/Slots, Docking, Property Editor, Resource System, i18n, Style Sheets, Accessibility | Ja, als Konzepte: Model/View, Docking, PropertyGrid, Ressourcen |
| **GTK** | CSS-Theming, ListModel, AT-SPI, Gestures, HeaderBar | Teilweise: Theming, Gestures, Accessibility |
| **wxWidgets** | Native Controls, AUI-Docking, Doc/View, Print | Ja: Docking, Doc/View, native Controls |
| **WinUI/WPF** | XAML, Data Binding, MVVM, Composition/Animation, High DPI, UIA | Ja: Binding, Animation, DPI, UIA |
| **Avalonia** | Cross-Platform, Styles, Data Templates, MVVM | Nein für Windows-Kern; Konzepte für Styling |
| **.NET MAUI** | Handler-Architektur, Shell, Cross-Platform | Nein; Handler-Idee für Backends |
| **SwiftUI** | Declarative State, Animation, Accessibility | Ja: State, Animation, Accessibility |
| **Flutter** | Widget-Komposition, Hot Reload, Custom Painting, Semantics | Ja: Hot Reload, Semantics, Custom Painting |
| **Electron** | Web-Tech, DevTools, IPC | Nein: keine Node/Chromium-Engine |
| **Tauri** | Webview + Rust-Kern | Nein: Webview-Abhängigkeit |
| **Dear ImGui** | Immediate Mode, Docking, Tools | Teilweise: Debug-UI, Docking-Ideen |
| **Dear PyGui** | GPU-Immediate-Mode | Nein: eigene GPU-Pipeline vorhanden |
| **Kivy** | Touch/Multitouch, KV-Sprache | Ja: Touch/Gesten, deklarative Sprache |
| **Slint** | Declarative UI, Embedded | Ja: deklarative Syntax, kleines Runtime |
| **egui** | Immediate Mode, Rust | Konzepte, keine Portierung |
| **LVGL** | Embedded-Widgets, Speicherarmut | Nein: Desktop-Framework |
| **JUCE** | Audio/MIDI, DSP, Plugin-Hosting | Ja: Audio/MIDI, Plugin-Konzepte |
| **SDL3** | Fenster, Renderer, GPU, Audio | Bereits genutzt |
| **Skia** | 2D-Rendering, Text, GPU | Konzepte; eigener Rasterizer bleibt |
| **HarfBuzz** | Text-Shaping | Konzepte; eigenes Shaping vorhanden |
| **Pango** | Text-Layout, i18n | Konzepte; eigenes Layout |
| **AccessKit** | Accessibility-Tree, plattformübergreifend | Ja: Tree-Modell, UIA/MSAA-Adapter |
| **Chromium** | Web-Engine | Nein |

## Prioritäten

### P0 – fehlende Kernkonzepte

1. **Model/View-Architektur**
   - `TableModel`, `TreeModel`, `ListModel`
   - Sortieren/Filteren/Editieren
   - Virtualisierung
   - Qt/WPF als Vorbild, eigene API

2. **Accessibility-Tree als zentrale Quelle**
   - bereits vorhanden: `AccessibilityTree`
   - Ausbau: Selection, TextRange, Strukturereignisse
   - AccessKit-Konzepte, keine Abhängigkeit

3. **Deklarative UI + State**
   - AMFW hat `amfw.quick`
   - AMFWX: `amfwx.quick` mit `State`/`QuickView`
   - Hot Reload für beide

### P1 – sichtbare Produktfeatures

4. **Animation/Composition**
   - Timeline, Easing, Transitions
   - WPF/SwiftUI/Flutter als Ideengeber

5. **Docking/PropertyGrid/Charts in AMFWX**
   - AMFW hat sie; AMFWX nicht
   - wxAUI/Qt als Vergleich

6. **Audio/MIDI**
   - WAV/MP4-Audio vorhanden
   - MIDI, DSP-Graph, VST3-Gastgeber wären JUCE-Niveau

7. **Plugin-/Resource-System**
   - Theme-Packs, Icons, Übersetzungen
   - Qt-Resource-Konzepte, eigene ZIP-Lösung

### P2 – Härtung

8. **Visuelle Regression**
   - Screenshot-Baselines
   - DPI-/Theme-Matrix
   - bereits teilweise vorhanden

9. **Fuzzing**
   - Parser: MP4, AVI, PNG, WebP, Fonts, Shader
   - bereits teilweise vorhanden

10. **Fehlerinjektion**
    - fehlende DLLs
    - ungültige Dateien
    - Speicher-/Handle-Leaks

## Was bewusst nicht kommt

- Electron/Node
- eingebettete Browser-Engine
- Cross-Platform-Cocoa/GTK im Kern
- vollständige CSS-Engine
- VST3/AU/AAX-Zertifizierung
- JavaScript-Engine

## Nächste konkrete Schritte

1. `TableModel`/`TreeModel` in AMFWX
2. `amfwx.quick` mit State/Hot Reload
3. Selection/TextRange im AccessibilityTree
4. Animations-Timeline
5. PropertyGrid und Charts für AMFWX
6. MIDI-Grundlage
