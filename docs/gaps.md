# AMFWX 3.1.0 – Gap-Analyse

Stand: 167 Tests, Windows-only. Öffentliche Signatur ist bewusst **kein Ziel**.

## Enthalten

- UI, Widgets, Layouts, Themes
- Text/OpenType/Arabisch/Bidi
- Editor, Docking, Charts, PropertyGrid
- UIA + MSAA + NVDA-Basis
- Model/View, QuickView/State
- Animation, MIDI, DSP, Mixer
- Video/Audio/Seek
- GPU/Compute
- Fuzzing, Snapshots, Crash-Logging, Plugins, Resources
- SDK: `create_sdk`, `UiSession`, LLM-Tools
- Ollama/OpenAI-kompatible Provider
- Streaming, Retry, Conversation-Persistenz, DPAPI-KeyStore
- Ollama-Modellverwaltung
- CI-Workflow, SBOM, Installer-Test
- AMFW-Bridges

## Bewusst nicht enthalten

- öffentliche Signatur / EV-Zertifikat
- SmartScreen-Reputation
- Cross-Platform
- VST3-Host

## Noch offen

| Punkt | Priorität | Status |
|---|---|---|
| AMFW-Bridge-Integrationstests | P0 | ❌ |
| echter Ollama-Test in CI | P0 | ⚠️ optional, nicht in CI |
| Compat-Adapter | P2 | ❌ |
| RichText/HTML-Subset | P2 | ❌ |
| weitere AMFW-Widgets | P2 | ❌ |
| Vision-/Bild-Eingabe | P2 | ❌ |
| MCP-Anbindung | P2 | ❌ |

## Nächste Schritte

1. Bridge-Integrationstests
2. Designer
3. PDF/Drucken
4. Quick/State vollständig
5. weitere Widgets

## Nicht mehr geplant

- öffentliche Signatur
- Cross-Platform
- VST3
