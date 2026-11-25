# Was noch fehlt

Stand: AMFWX 5.46.0 – 433 Tests

## Nur noch Hardware

| Punkt | Status |
|---|---|
| UVC-Kamera real | ❌ keine Kamera verfügbar |
| ONVIF/RTSP real | ❌ keine Kamera verfügbar |
| Tuya 3.4/3.5 real | ❌ nur Fake-Server |
| Matter real | ❌ nur chip-tool/Fake |
| Becker-Stick real | ❌ nicht angeschlossen |
| Jarolift-ESP32 real | ❌ nicht angeschlossen |
| IPP-Drucker | ❌ Kyocera bietet keinen Endpunkt |
| Druck-Finishing | ❌ treiberabhängig |

## Kamera-SDKs

| Hersteller | Status |
|---|---|
| Canon EDSDK | ❌ nicht gebündelt |
| Nikon SDK | ❌ |
| Sony Camera Remote SDK | ❌ |
| Fuji/Olympus/Leica | ❌ |
| DJI native | ❌ nur MTP/UVC |
| gPhoto2 | ✅ optional extern |
| GoPro | ✅ HTTP |

Die Plugin-API ist vorhanden; die SDK-Adapter fehlen.

## SDK / LLM

| Punkt | Status |
|---|---|
| `amfwx-sdk` | ✅ |
| `amfwx-mcp` | ✅ |
| UI-/App-Tools | ✅ mit Opt-in |
| MCP-Tools/Ressourcen/Prompts | ✅ |
| Streaming/Cancel/Async | ✅ |
| Provider-Plugins | ✅ |
| 32-Bit-Runtime im Wheel | ✅ |
| Home-/Tuya-/Matter-Tools für LLM | ❌ |
| App-Tool-Timeouts | ⚠️ teilweise |
| SDK-Beispiele im Wheel | ❌ |

## Scanner

| Punkt | Status |
|---|---|
| WIA/TWAIN 32/64 | ✅ |
| NAPS2-Adapter + ADF | ✅ |
| Scanner-Fenster + Profile | ✅ |
| Deskew/Crop/Blank-Pages | ✅ |
| Scan → OCR-PDF | ✅ |
| NAPS2 real | ✅ |
| Treiberpakete bündeln | ❌ Herstellersache |
| Scanner-Duplex profile | ⚠️ treiberabhängig |

## Drucken

| Punkt | Status |
|---|---|
| Windows Queue + GDI | ✅ |
| TCP 9100 | ✅ real |
| IPP Client | ✅ |
| Kopien/Duplex/Papier/Querformat | ✅ |
| Vorschau | ✅ |
| Druck-Profile | ✅ |
| Finishing/Stapling | ❌ |
| Signatur | ❌ bewusst |

## UI / Framework

| Punkt | Status |
|---|---|
| Dashboard | ✅ Aktionen |
| Scanner-/Kamera-Fenster | ✅ |
| Druckvorschau | ✅ |
| i18n | ❌ |
| IME | ❌ |
| Kalender/Datum/Zeit | ❌ |
| Completer | ❌ |
| Toasts/Splash | ❌ |
| OLE-Drop | ❌ |
| WebSocket/HTTP-Server | ❌ |
| editierbares Model/View | ⚠️ Basis |

## Infrastruktur

| Punkt | Status |
|---|---|
| 433 Tests | ✅ |
| CI-Matrix 3.10–3.13 | ✅ |
| 32-Bit im CI | ✅ |
| Hardware-Smoke | ✅ `tools/hardware_smoke.py` |
| Optionale Extras | ✅ `[scanner]`, `[camera]`, `[ocr]`, `[pdf]`, `[iot]`, `[full]` |
| Auto-Update-Ausführung | ❌ nur Prüfung/Download |
| Signatur | ❌ bewusst |

## Sinnvolle Reihenfolge

1. Echte Hardwaretests
2. Kamera-SDK-Adapter
3. App-Tool-Timeouts
4. Home-/Tuya-/Matter-Tools für LLM
5. Druck-Finishing
6. i18n/IME/Kalender/WebSocket, falls AMFW-Parität Ziel ist
