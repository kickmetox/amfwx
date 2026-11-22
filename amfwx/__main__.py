"""AMFWX demo entry point."""

from . import Button, BoxLayout, Label, LineEdit, Window


def main():
    window = Window("AMFWX", 720, 480)
    window.layout = BoxLayout(spacing=10, padding=20)
    window.root.children.clear()
    items = [
        Label("AMFWX", scale=4),
        Label("Eigener Rasterizer. Eigene Widgets.", scale=2),
        LineEdit("Text"),
        Button("Beenden", on_click=window.close, variant="primary"),
    ]
    for item in items:
        window.root.add(item)
        window.layout.add(item)
    window._layout_root()
    window.invalidate()
    return window.run()


if __name__ == "__main__":
    raise SystemExit(main())
