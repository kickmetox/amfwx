"""AMFWX demo application entry point."""

from __future__ import annotations

from amfwx import Button, BoxLayout, Label, LineEdit, Window
from amfwx.application import AppConfig, Application
from amfwx.crash import CrashLogger


def create_window(config):
    window = Window(config.title, config.width, config.height,
                    theme=config.theme)
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
    return window


def main(argv=None):
    config = AppConfig.parse(argv)
    logger = CrashLogger().install()
    try:
        app = Application(config,
                          window_factory=lambda: create_window(config))
        return app.run()
    finally:
        logger.uninstall()


if __name__ == "__main__":
    raise SystemExit(main())
