# AMFWX 3.0.0 – Gap-Analyse

Stand: 162 Tests, Release 3.0.0, Windows-only.

## Enthalten

- UI, Widgets, Layouts, Themes
- Text/OpenType/Arabisch/Bidi
- Editor, Docking, Charts, PropertyGrid
- UIA + MSAA + NVDA-Basis
- Model/View, QuickView/State
- Animation, MIDI, DSP, Mixer
- Video/Audio/Seek
- GPU/Compute
- Fuzzing, Snapshots
- Crash-Logging, Plugin-Registry, Resources
- SDK: `create_sdk`, `UiSession`, LLM-Tools
- Ollama-/OpenAI-kompatible Provider
- AMFWX-in-AMFW- und AMFW-in-AMFWX-Bridge

## Fehlt für einen belastbaren Release

| Punkt | Priorität | Status |
|---|---|---|
| CI-Workflow (Tests + Build) | P0 | ❌ entfernt |
| Installer-3.0.0-Silent-Test | P0 | ⚠️ nicht erneut geprüft |
| AMFW-Bridge-Integrationstests | P0 | ❌ |
| Echter Ollama-End-to-End-Test | P0 | ❌ nur HTTP-Mock |
| SBOM/Lizenzübersicht | P1 | ❌ |
| Release-Doku 3.0.0 vollständig | P1 | ⚠️ Basis vorhanden |
| öffentliche Signatur | Distributor | ❌ optional |

## AMFW-Funktionen, die in AMFWX fehlen

| Funktion | Aufwand |
|---|---|
| Designer | mittel–groß |
| Studio/Projektstarter | mittel |
| vollständiges `amfw.quick` | groß |
| Compat-Adapter (Tkinter/GTK/wx/FLTK/JUCE/Flutter/MAUI/SwiftUI/ImGui/Electron) | sehr groß |
| PDF/Drucken | mittel |
| Datenbank/Netzwerk | mittel |
| RichText/HTML-Subset | groß |
| ~80 AMFW-Widgets | groß |
| GDI+-Painter-Äquivalent | nicht 1:1 |

## SDK/LLM-Lücken

- kein Streaming
- keine Vision-/Bild-Eingabe
- keine Gesprächspersistenz
- kein Retry/Backoff
- kein Modell-Management (Pull/Delete)
- kein Tool-Fallback für Modelle ohne Tool-Calling
- keine MCP-Anbindung
- kein sicherer Key-Store (nur Env/Parameter)
- keine Token-/Kostenanzeige
- keine automatischen UI-Tests durch das Modell
- Tool-Set deckt nur 7 Widget-Typen ab

## Plattform

- Windows-only
- H.264/MP4 über Media Foundation
- kein VST3-Host
- kein MSI/Auto-Update
- keine öffentliche Signatur

## Nächste Schritte

### P0

1. CI-Workflow ohne SignPath
2. Installer 3.0.0 testen
3. Bridge-Tests
4. echter Ollama-Test

### P1

5. SBOM
6. AI-Streaming
7. Designer/Quick/PDF portieren
8. Release-Doku

### P2

9. VST3/DSP
10. Cross-Platform
