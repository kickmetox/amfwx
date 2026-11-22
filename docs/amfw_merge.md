# AMFW-Funktionen nach AMFWX: Ein Paket vs. eine Engine

## Kurzfassung

- **Ein Distributionspaket** mit AMFW + AMFWX: machbar.
- **Eine gemeinsame Engine**, die alle AMFW-Funktionen in AMFWX nachbaut:
  technisch möglich, aber nicht in einem Schritt und nicht 1:1.

## Was schon verbindet

- `AmfwxView`: AMFWX-Widgets als Bild in AMFW
- `AmfwxWindowHost`: AMFW-Fenster als natives Child in AMFWX
- gleicher Win32-UI-Thread
- optionale Abhängigkeit, kein Zwang

## Feature-Lücken

| AMFW-Funktion | In AMFWX | Aufwand |
|---|---|---|
| Designer | nein | mittel–groß |
| Studio/Projektstarter | nein | mittel |
| `amfw.quick` (voll) | nur QuickView/State | groß |
| Compat-Adapter (Tkinter/GTK/wx/FLTK/JUCE/Flutter/MAUI/SwiftUI/ImGui/Electron) | nein | sehr groß |
| PDF/Drucken | nein | mittel |
| Datenbank/Netzwerk | nein | mittel |
| RichText/HTML-Subset | nein | groß |
| native Menüs/Toolbars | teilweise | klein–mittel |
| ~80 Widgets | ~30 | groß |
| GDI+-Painter | eigener BGRA-Rasterizer | nicht portierbar |
| AMFW-Compat-Semantik | nein | nicht sinnvoll 1:1 |

## Warum nicht einfach kopieren

AMFW und AMFWX haben unterschiedliche Architekturen:

- AMFW: GDI+, eigene gezeichnete Widgets, Win32-Fenster
- AMFWX: BGRA-Rasterizer, eigene Layout-/Paint-Pipeline

Ein Widget ist deshalb nicht nur eine Klasse, sondern:

- Layout
- Painter
- Theme
- Fokus
- Accessibility
- DPI
- Event-Weitergabe

Ein 1:1-Port wäre ein Neuschreiben der Widgets.

## Empfohlener Weg

### Phase 1: Ein Paket

Ein Installer/Meta-Paket mit:

- `amfw`
- `amfwx`
- `amfwx.amfw_bridge`
- gemeinsamen Beispielen
- gemeinsamer Doku

Das ist die schnellste Lösung für „ein Paket“.

### Phase 2: AMFWX als Kern

Nach AMFWX portieren:

1. Designer
2. Druck/PDF
3. vollständiges Quick/State
4. RichText
5. Netzwerk/DB
6. weitere Widgets

### Phase 3: Kompatibilität

Compat-Adapter nur portieren, wenn sie wirklich gebraucht werden.
Sie sind eher ein Ökosystem als ein Framework-Kern.

## Empfehlung

- **Ein Paket:** ja, sofort machbar.
- **Eine Engine:** AMFWX als Zielarchitektur, AMFW als optionale Legacy-/Native-Insel.
- **Accessibility:** nicht mischen; ein Framework muss führen.
- **Designer/Quick/PDF:** zuerst portieren, weil sie sichtbaren Nutzen bringen.

## Status

Die Bridges sind vorhanden, aber nicht Teil der automatisierten Tests.
Vor einem „ein Paket“-Release müssen Fokus, DPI, Screenreader und Leaks
getestet werden.
