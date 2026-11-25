"""Camera window: live preview, snapshot, recording and tethering."""

from __future__ import annotations

import threading
import time
from pathlib import Path

from .advanced import ImageView
from .camera import Webcam
from .quick import HStack
from .scan_transfer import default_scan_dir
from .profiles import ProfileStore
from .widgets import BoxLayout, Button, CheckBox, ComboBox, Label, LineEdit
from .window import Window


class CameraWindow(Window):
    def __init__(self):
        super().__init__("AMFWX Kamera", 820, 660)
        self.profile = ComboBox([], 0)
        self.profile_name = LineEdit("", placeholder="Profilname")
        self.profile_store = ProfileStore()
        self.save_profile_button = Button("Profil speichern",
                                          on_click=self.save_profile)
        self.load_profile_button = Button("Profil laden",
                                          on_click=self.load_profile)
        self.index = LineEdit("0")
        self.url = LineEdit("", placeholder="rtsp://...")
        self.width = LineEdit("1280")
        self.height = LineEdit("720")
        self.folder = LineEdit(str(default_scan_dir()))
        self.frames = LineEdit("5")
        self.interval = LineEdit("2")
        self.seconds = LineEdit("5")
        self.brightness = LineEdit("", placeholder="auto")
        self.contrast = LineEdit("", placeholder="auto")
        self.exposure = LineEdit("", placeholder="auto")
        self.focus = LineEdit("", placeholder="auto")
        self.chroma = CheckBox("Chroma Key (grün)", checked=False)
        self.preview = ImageView(fit=True)
        self.status = Label("Bereit.")
        self.preview_button = Button("Vorschau", on_click=self.toggle_preview,
                                     variant="secondary")
        self.snapshot_button = Button("Einzelbild", on_click=self.snapshot)
        self.record_button = Button("Aufnehmen", on_click=self.record)
        self.apply_button = Button("Einstellungen", on_click=self.apply_controls)
        self.tether_button = Button("Tethering", on_click=self.tether,
                                    variant="primary")
        self.close_button = Button("Schließen", on_click=self.close)
        self.layout = BoxLayout("vertical", spacing=6, padding=12)
        self.root.children.clear()
        self.layout.items.clear()
        rows = [
            HStack(Label("Profil"), self.profile, self.profile_name,
                   self.save_profile_button, self.load_profile_button),
            self.preview,
            HStack(Label("Index"), self.index),
            HStack(Label("IP/RTSP"), self.url),
            HStack(Label("Breite"), self.width),
            HStack(Label("Höhe"), self.height),
            HStack(Label("Ordner"), self.folder),
            HStack(Label("Aufnahmen"), self.frames),
            HStack(Label("Intervall"), self.interval),
            HStack(Label("Video-Sekunden"), self.seconds),
            HStack(Label("Helligkeit"), self.brightness),
            HStack(Label("Kontrast"), self.contrast),
            HStack(Label("Belichtung"), self.exposure),
            HStack(Label("Fokus"), self.focus),
            self.chroma,
            self.status,
            HStack(self.preview_button, self.snapshot_button,
                   self.record_button, self.apply_button),
            HStack(self.tether_button, self.close_button),
        ]
        for row in rows:
            self.root.add(row)
            self.layout.add(row)
        self._layout_root()
        self.invalidate()
        self._previewing = False
        self._preview_camera = None
        self._refresh_profiles()

    def _refresh_profiles(self):
        self.profile.items = self.profile_store.names("camera")
        if self.profile.items:
            self.profile.current_index = 0

    def _profile_values(self):
        return {
            "index": self.index.text(),
            "url": self.url.text(),
            "width": self.width.text(),
            "height": self.height.text(),
            "folder": self.folder.text(),
            "frames": self.frames.text(),
            "interval": self.interval.text(),
            "seconds": self.seconds.text(),
            "chroma": self.chroma.checked,
            "brightness": self.brightness.text(),
            "contrast": self.contrast.text(),
            "exposure": self.exposure.text(),
            "focus": self.focus.text(),
        }

    def save_profile(self):
        name = (self.profile_name.text().strip() or
                self.profile.current_text())
        if not name:
            self.status.text = "Kein Profilname vorhanden."
            self.invalidate()
            return
        self.profile_store.save("camera", name, self._profile_values())
        self.profile_name.set_text(name)
        self._refresh_profiles()
        self.status.text = f"Profil gespeichert: {name}"
        self.invalidate()

    def load_profile(self):
        name = self.profile.current_text()
        if not name:
            return
        try:
            values = self.profile_store.load("camera", name)
        except Exception as error:
            self.status.text = f"Profilfehler: {error}"
            self.invalidate()
            return
        for widget, key in ((self.index, "index"), (self.url, "url"),
                            (self.width, "width"), (self.height, "height"),
                            (self.folder, "folder"), (self.frames, "frames"),
                            (self.interval, "interval"),
                            (self.seconds, "seconds"),
                            (self.brightness, "brightness"),
                            (self.contrast, "contrast"),
                            (self.exposure, "exposure"),
                            (self.focus, "focus")):
            widget.set_text(values.get(key, widget.text()))
        self.chroma.checked = bool(values.get("chroma", self.chroma.checked))
        self.status.text = f"Profil geladen: {name}"
        self.invalidate()

    def _camera(self):
        if self.url.text().strip():
            from .ipcam import IpCamera
            return IpCamera(self.url.text().strip(),
                            width=int(self.width.text() or "1280"),
                            height=int(self.height.text() or "720"))
        return Webcam(int(self.index.text() or "0"),
                      width=int(self.width.text() or "1280"),
                      height=int(self.height.text() or "720"))

    def _set_preview(self, image):
        self.preview.image = image
        self.preview._cache_key = None
        self.invalidate()

    def start_preview(self):
        if self._previewing:
            return
        try:
            camera = self._camera()
        except Exception as error:
            self.status.text = f"Vorschau-Fehler: {error}"
            self.invalidate()
            return
        self._previewing = True
        self._preview_camera = camera
        self.preview_button.text = "Vorschau stoppen"
        self.status.text = "Vorschau läuft."
        self.invalidate()

        def work():
            while self._previewing:
                try:
                    image = camera.read()
                except Exception as error:
                    self.invoke(lambda: self._preview_error(str(error)))
                    return
                self.invoke(lambda img=image: self._set_preview(img))
                time.sleep(1 / 15)

        threading.Thread(target=work, daemon=True).start()

    def _preview_error(self, message):
        self.status.text = f"Vorschau: {message}"
        self.stop_preview()

    def stop_preview(self):
        self._previewing = False
        camera, self._preview_camera = self._preview_camera, None
        if camera is not None:
            try:
                camera.close()
            except Exception:
                pass
        self.preview_button.text = "Vorschau"
        self.invalidate()

    def toggle_preview(self):
        if self._previewing:
            self.stop_preview()
            self.status.text = "Vorschau gestoppt."
        else:
            self.start_preview()

    def apply_controls(self):
        values = {
            "brightness": self.brightness.text().strip(),
            "contrast": self.contrast.text().strip(),
            "exposure": self.exposure.text().strip(),
            "focus": self.focus.text().strip(),
        }
        try:
            camera = self._camera()
            try:
                applied = []
                for name, text in values.items():
                    if text:
                        camera.set_control(name, float(text))
                        applied.append(name)
            finally:
                camera.close()
        except Exception as error:
            self.status.text = f"Einstellungsfehler: {error}"
        else:
            self.status.text = ("Gesetzt: " + ", ".join(applied)
                                if applied else "Keine Werte gesetzt.")
        self.invalidate()

    def snapshot(self):
        self.stop_preview()
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

    def record(self):
        self.stop_preview()
        try:
            folder = Path(self.folder.text().strip() or default_scan_dir())
            folder.mkdir(parents=True, exist_ok=True)
            target = folder / f"video_{time.strftime('%Y%m%d_%H%M%S')}.avi"
            seconds = max(1.0, float(self.seconds.text() or "5"))
        except ValueError as error:
            self.status.text = f"Eingabefehler: {error}"
            self.invalidate()
            return
        self.status.text = "Aufnahme läuft..."
        self.invalidate()

        def work():
            try:
                camera = self._camera()
                try:
                    camera.record(target, seconds)
                finally:
                    camera.close()
            except Exception as error:
                self.invoke(lambda: self._done([], str(error)))
            else:
                self.invoke(lambda: self._done([str(target)], None))

        threading.Thread(target=work, daemon=True).start()

    def tether(self):
        self.stop_preview()
        self.tether_button.enabled = False
        self.status.text = "Tethering läuft..."
        self.invalidate()
        try:
            index = int(self.index.text() or "0")
            url = self.url.text().strip()
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
                if url:
                    from .ipcam import IpCamera
                    camera = IpCamera(url, width=width, height=height)
                else:
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

    def close(self):
        self.stop_preview()
        super().close()
