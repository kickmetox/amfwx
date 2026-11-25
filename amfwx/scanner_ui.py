"""Scanner window for WIA, TWAIN32 and NAPS2."""

from __future__ import annotations

import tempfile
import threading
import time
from pathlib import Path

from .quick import HStack
from .scan_pdf import images_to_pdf
from .scan_transfer import default_scan_dir
from .profiles import ProfileStore
from .widgets import BoxLayout, Button, CheckBox, ComboBox, Label, LineEdit
from .window import Window


class ScannerWindow(Window):
    def __init__(self):
        super().__init__("AMFWX Scanner", 760, 480)
        self.backend = ComboBox(["WIA", "TWAIN32", "NAPS2"], 0)
        self.profile = ComboBox([], 0)
        self.profile_name = LineEdit("", placeholder="Profilname")
        self.profile_store = ProfileStore()
        self.save_profile_button = Button("Profil speichern",
                                          on_click=self.save_profile)
        self.load_profile_button = Button("Profil laden",
                                          on_click=self.load_profile)
        self.source = ComboBox([], 0)
        self.folder = LineEdit(str(default_scan_dir()))
        self.dpi = LineEdit("300")
        self.pdf = CheckBox("Als PDF speichern", checked=True)
        self.ocr = CheckBox("Durchsuchbares PDF (OCR)", checked=False)
        self.language = LineEdit("de-DE")
        self.adf = CheckBox("Einzug (ADF)", checked=False)
        self.deskew = CheckBox("Geraderichten", checked=True)
        self.crop = CheckBox("Zuschneiden", checked=True)
        self.drop_blank = CheckBox("Leere Seiten entfernen", checked=False)
        self.status = Label("Quellen laden...")
        self.refresh_button = Button("Quellen", on_click=self.refresh,
                                     variant="secondary")
        self.scan_button = Button("Scannen", on_click=self.scan,
                                  variant="primary")
        self.close_button = Button("Schließen", on_click=self.close)
        self.layout = BoxLayout("vertical", spacing=6, padding=12)
        self.root.children.clear()
        self.layout.items.clear()
        for row in [
            HStack(Label("Profil"), self.profile, self.profile_name,
                   self.save_profile_button, self.load_profile_button),
            HStack(Label("Backend"), self.backend, self.refresh_button),
            HStack(Label("Quelle"), self.source),
            HStack(Label("Ordner"), self.folder),
            HStack(Label("DPI"), self.dpi),
            self.adf, self.deskew, self.crop, self.drop_blank,
            self.pdf, self.ocr,
            HStack(Label("OCR-Sprache"), self.language),
            self.status,
            HStack(self.scan_button, self.close_button),
        ]:
            self.root.add(row)
            self.layout.add(row)
        self._layout_root()
        self.invalidate()
        self._refresh_profiles()
        self.refresh()

    def _refresh_profiles(self):
        self.profile.items = self.profile_store.names("scanner")
        if self.profile.items:
            self.profile.current_index = 0

    def _profile_values(self):
        return {
            "backend": self.backend.current_text(),
            "source": self.source.current_text(),
            "folder": self.folder.text(),
            "dpi": self.dpi.text(),
            "pdf": self.pdf.checked,
            "ocr": self.ocr.checked,
            "language": self.language.text(),
            "adf": self.adf.checked,
            "deskew": self.deskew.checked,
            "crop": self.crop.checked,
            "drop_blank": self.drop_blank.checked,
        }

    def save_profile(self):
        name = (self.profile_name.text().strip() or
                self.profile.current_text())
        if not name:
            self.status.text = "Kein Profilname vorhanden."
            self.invalidate()
            return
        self.profile_store.save("scanner", name, self._profile_values())
        self.profile_name.set_text(name)
        self._refresh_profiles()
        self.status.text = f"Profil gespeichert: {name}"
        self.invalidate()

    def load_profile(self):
        name = (self.profile_name.text().strip() or
                self.profile.current_text())
        if not name:
            return
        try:
            values = self.profile_store.load("scanner", name)
        except Exception as error:
            self.status.text = f"Profilfehler: {error}"
            self.invalidate()
            return
        self.folder.set_text(values.get("folder", self.folder.text()))
        self.dpi.set_text(values.get("dpi", self.dpi.text()))
        self.language.set_text(values.get("language", self.language.text()))
        for widget, key in ((self.pdf, "pdf"), (self.ocr, "ocr"),
                            (self.adf, "adf"), (self.deskew, "deskew"),
                            (self.crop, "crop"),
                            (self.drop_blank, "drop_blank")):
            if hasattr(widget, "checked"):
                widget.checked = bool(values.get(key, widget.checked))
        self.status.text = f"Profil geladen: {name}"
        self.invalidate()

    def _backend(self):
        return self.backend.current_text().lower()

    def refresh(self):
        self.status.text = "Quellen laden..."
        self.invalidate()
        backend = self._backend()

        def work():
            try:
                if backend == "wia":
                    from .wia import list_wia_devices
                    items = [(device.name, device.device_id)
                             for device in list_wia_devices()]
                elif backend == "twain32":
                    from .twain32 import list_sources
                    items = [(source.name, source.name)
                             for source in list_sources()]
                else:
                    from .naps2 import list_sources
                    items = [(source.id, source.id)
                             for source in list_sources()]
            except Exception as error:
                self.invoke(lambda: self._sources([], str(error)))
            else:
                self.invoke(lambda: self._sources(items, None))

        threading.Thread(target=work, daemon=True).start()

    def _sources(self, items, error):
        self._source_map = dict(items)
        self.source.items = [name for name, _value in items]
        self.source.current_index = 0
        if error:
            self.status.text = f"Quellenfehler: {error}"
        elif not items:
            self.status.text = "Keine Quellen gefunden."
        else:
            self.status.text = f"{len(items)} Quelle(n)."
        self.invalidate()

    def scan(self):
        self.scan_button.enabled = False
        try:
            folder = Path(self.folder.text().strip() or default_scan_dir())
            dpi = max(50, int(self.dpi.text() or "300"))
            source = self._source_map.get(self.source.current_text(), "")
            if not source:
                raise RuntimeError("keine Quelle gewählt")
            backend = self._backend()
            use_ocr = self.ocr.checked
            use_pdf = self.pdf.checked or use_ocr
            language = self.language.text().strip() or None
            adf = self.adf.checked
            postprocess_options = {
                "deskew_enabled": self.deskew.checked,
                "crop_enabled": self.crop.checked,
                "drop_blank": self.drop_blank.checked,
            }
        except Exception as error:
            self.status.text = f"Eingabefehler: {error}"
            self.scan_button.enabled = True
            self.invalidate()
            return
        self.status.text = "Scan läuft..."
        self.invalidate()

        def work():
            try:
                with tempfile.TemporaryDirectory(prefix="amfwx_scanui_") as temp:
                    raw = str(Path(temp) / "page")
                    if backend == "wia":
                        from .wia import WiaScanner
                        result = WiaScanner(device_id=source).acquire(
                            raw + ".png", dpi=dpi, adf=adf)
                    elif backend == "twain32":
                        from .twain32 import scan
                        result = scan(source, raw + ".png")
                    else:
                        from .naps2 import Naps2Scanner
                        scanner = Naps2Scanner()
                        if adf:
                            result = scanner.scan_batch(source, temp, dpi=dpi)
                        else:
                            result = scanner.scan(
                                source, raw + ".jpg", dpi=dpi,
                                paper_source="Glass")
                    images = result if isinstance(result, list) else [result]
                    from PIL import Image
                    jpgs = []
                    for number, item in enumerate(images, 1):
                        target = Path(temp) / f"page_{number:03d}.jpg"
                        Image.open(item).convert("RGB").save(
                            target, "JPEG", quality=92)
                        jpgs.append(target)
                    from .scan_post import postprocess_pages
                    jpgs = postprocess_pages(jpgs, **postprocess_options)
                    folder.mkdir(parents=True, exist_ok=True)
                    stem = f"scan_{time.strftime('%Y%m%d_%H%M%S')}"
                    if use_pdf:
                        output = folder / f"{stem}.pdf"
                        images_to_pdf(jpgs, output)
                        if use_ocr:
                            from .ocr import make_searchable_pdf
                            output = make_searchable_pdf(
                                output, folder / f"{stem}_searchable.pdf",
                                language)
                        files = [str(output)]
                    else:
                        output = folder / f"{stem}.jpg"
                        jpgs[0].replace(output)
                        files = [str(output)]
            except Exception as error:
                self.invoke(lambda: self._done([], str(error)))
            else:
                self.invoke(lambda: self._done(files, None))

        threading.Thread(target=work, daemon=True).start()

    def _done(self, files, error):
        self.scan_button.enabled = True
        if error:
            self.status.text = f"Fehler: {error}"
        else:
            self.status.text = "Fertig: " + ", ".join(files)
        self.invalidate()
