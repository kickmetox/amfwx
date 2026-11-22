"""Minimal AMFWX demo."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from amfwx import BoxLayout, Button, Color, Label, Window


def main():
    window = Window("AMFWX", 760, 480)
    window.canvas.clear(Color(20, 22, 28))
    layout = BoxLayout(spacing=10, padding=24)
    layout.add(Label("AMFWX", scale=4), 0)
    layout.add(Label("Eigener Rasterizer. Eigene Widgets.", scale=2), 0)
    button = Button("Klick mich", on_click=lambda: print("clicked"))
    layout.add(button, 0)
    window.layout = layout
    window.root.children.clear()
    for widget, _stretch in layout.items:
        window.root.add(widget)
    window._layout_root()
    window.invalidate()
    return window.run()


if __name__ == "__main__":
    raise SystemExit(main())
