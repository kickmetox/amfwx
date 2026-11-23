"""Camera window: snapshot, tethering and chroma key."""

from __future__ import annotations

import threading
import time
from pathlib import Path

from .camera import Webcam
from .quick import HStack
from .scan_transfer import default_scan_dir
from .widgets import BoxLayout, Button, CheckBox, Label, LineEdit
from .window import Window


class CameraWindow(Window):
    def __init__(self):
        super().__init__("AMFWX Kamera", 760, 460)
        self.index = LineEdit("0")
        self.width = LineEdit("1280")
        self.height = LineEdit("720")
        self.folder = LineEdit(str(default_scan_dir()))
        self.frames = LineEdit("5")
        self.interval = LineEdit("2")
        self.chroma = CheckBox("Chroma Key (grün)", checked=False)
        self.status = Label("Bereit.")
        self.snapshot_button = Button("Einzelbild", on_click=self.snapshot)
        self.tether_button = Button("Tethering", on_click=self.tether,
                                    variant="primary")
        self.close_button = Button("Schließen", on_click=self.close)
        self.layout = BoxLayout("vertical", spacing=6, padding=12)
        self.root.children.clear()
        self.layout.items.clear()
        rows = [
            HStack(Label("Index"), self.index),
            HStack(Label("Breite"), self.width),
            HStack(Label("Höhe"), self.height),
            HStack(Label("Ordner"), self.folder),
            HStack(Label("Aufnahmen"), self.frames),
            HStack(Label("Intervall"), self.interval),
            self.chroma,
            self.status,
            HStack(self.snapshot_button, self.tether_button,
                   self.close_button),
        ]
        for row in rows:
            self.root.add(row)
            self.layout.add(row)
        self._layout_root()
        self.invalidate()

    def _camera(self):
        return Webcam(int(self.index.text() or "0"),
                      width=int(self.width.text() or "1280"),
                      height=int(self.height.text() or "720"))

    def snapshot(self):
        self.status.text = "Aufnahme..."
        self.invalidate()
        try:
            camera = self._camera()
            try:
                image = camera.read()
                folder = Path(self.folder.text().strip() or default_scan_dir())
                folder.mkdir(parents=True, exist_ok=True)
                target = folder / f"camera_{time.strftime('%Y%m%d_%H%M%S')}.jpg"
                image.save(target)
            finally:
                camera.close()
        except Exception as error:
            self.status.text = f"Fehler: {error}"
        else:
            self.status.text = f"Gespeichert: {target}"
        self.invalidate()

    def tether(self):
        self.tether_button.enabled = False
        self.status.text = "Tethering läuft..."
        self.invalidate()
        try:
            index = int(self.index.text() or "0")
            width = int(self.width.text() or "1280")
            height = int(self.height.text() or "720")
            folder = self.folder.text().strip() or str(default_scan_dir())
            count = max(1, int(self.frames.text() or "1"))
            interval = max(0.0, float(self.interval.text() or "0"))
            chroma = (0, 255, 0) if self.chroma.checked else None
        except ValueError as error:
            self.status.text = f"Eingabefehler: {error}"
            self.tether_button.enabled = True
            self.invalidate()
            return

        def work():
            try:
                camera = Webcam(index, width=width, height=height)
                try:
                    files = camera.tether(folder, count=count,
                                          interval=interval,
                                          chroma_key=chroma)
                finally:
                    camera.close()
            except Exception as error:
                self.invoke(lambda: self._done([], str(error)))
            else:
                self.invoke(lambda: self._done(files, None))

        threading.Thread(target=work, daemon=True).start()

    def _done(self, files, error):
        self.tether_button.enabled = True
        if error:
            self.status.text = f"Fehler: {error}"
        else:
            self.status.text = f"Fertig: {len(files)} Aufnahme(n)"
        self.invalidate()
