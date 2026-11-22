# AMFW in AMFWX integrieren

Es gibt zwei Richtungen. Beide laufen im selben Win32-UI-Thread und
brauchen keinen zweiten Eventloop.

## 1. AMFWX-Widgets in einem AMFW-Fenster

`amfwx.amfw_bridge.AmfwxView` ist ein AMFW-Widget, das einen AMFWX-Widget-Baum
in ein RGBA-Bild rendert.

```python
import sys
sys.path.insert(0, r"D:\AI_Temp\AMFW")

from amfw import Window
from amfwx import Label
from amfwx.amfw_bridge import AmfwxView

window = Window("AMFW + AMFWX", 640, 420)
view = AmfwxView(Label("Hallo aus AMFWX"), 400, 120)
window.add(view)
window.run()
```

Eigenschaften:

- AMFW behält Fenster, Eventloop und native Controls.
- AMFWX liefert Rasterizer und Widgets.
- Maus/Tastatur werden an den AMFWX-Baum weitergereicht.
- Es gibt keine zweite Message-Loop.

Grenzen:

- AMFWX wird als Bitmap gezeichnet, nicht als native Controls.
- Screenreader sehen die AMFWX-Widgets dort nicht als eigene Controls.
- DPI-Skalierung kann unscharf werden.
- Fokus/Tab muss die AMFWX-Bridge selbst weiterleiten.

## 2. AMFW-Fenster in einem AMFWX-Fenster

`amfwx.amfw_bridge.AmfwxWindowHost` hängt ein echtes AMFW-Fenster als
nativen Child in ein AMFWX-Fenster.

```python
import sys
sys.path.insert(0, r"D:\AI_Temp\AMFW")

import amfw
from amfwx import Window
from amfwx.amfw_bridge import AmfwxWindowHost

host = Window("AMFWX Host", 800, 600)
amfw_window = amfw.Window("AMFW Child", 600, 400)
AmfwxWindowHost(amfw_window).attach(host)
host.run()
```

Eigenschaften:

- AMFW-Fenster bleibt ein echtes natives Fenster.
- AMFWX pumpt die Nachrichten.
- Native AMFW-Controls und deren Accessibility bleiben eher erhalten.

Grenzen:

- `SetParent` ändert Fensterstil und Fokusverhalten.
- Gemeinsame Menüs/Dialoge müssen koordiniert werden.
- Kein gemeinsames Theming.
- Zwei UI-Frameworks bedeuten zwei Fehlerquellen.

## Voraussetzungen

- AMFW und AMFWX müssen importierbar sein.
- Beide müssen im selben Prozess und UI-Thread laufen.
- Die Bridge ist optional; AMFWX importiert AMFW nur bei Nutzung.

## Empfehlung

- Für **native Controls/Accessibility**: AMFW außen, AMFWX nur als
  eingebettete Zeichenfläche.
- Für **eigene AMFWX-UI**: AMFWX außen, AMFW als native Child-Insel.
- Für **eine durchgängige Accessibility-Struktur**: nicht mischen; eines
  der beiden Frameworks vollständig verwenden.

## Status

Die Bridges sind vorhanden und importierbar, aber nicht Teil der
automatisierten AMFWX-Test-Suite. Vor Produktnutzung:

1. Fokus/Tab testen
2. DPI-Wechsel testen
3. Screenreader-Test
4. Speicher-/Handle-Leaks prüfen
