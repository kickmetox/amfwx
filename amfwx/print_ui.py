"""Print preview window."""

from __future__ import annotations

from pathlib import Path

from .advanced import ImageView
from .pdf_print import print_pdf, render_pdf
from .quick import HStack
from .widgets import BoxLayout, Button, CheckBox, ComboBox, Label, LineEdit
from .profiles import ProfileStore
from .window import Window


class PrintPreviewWindow(Window):
    def __init__(self, pdf_path=None, printer_name=None):
        super().__init__("AMFWX Druckvorschau", 820, 720)
        self.pdf_path = str(pdf_path or "")
        self.printer_name = str(printer_name or "")
        self.preview = ImageView(fit=True)
        self.profile = ComboBox([], 0)
        self.profile_name = LineEdit("", placeholder="Profilname")
        self.profile_store = ProfileStore()
        self.save_profile_button = Button("Profil speichern",
                                          on_click=self.save_profile)
        self.load_profile_button = Button("Profil laden",
                                          on_click=self.load_profile)
        self.paper = ComboBox(["A4", "A5", "A3", "Letter", "Legal"], 0)
        self.copies = LineEdit("1")
        self.duplex = CheckBox("Duplex", checked=False)
        self.landscape = CheckBox("Querformat", checked=False)
        self.status = Label(self.pdf_path or "Keine PDF gewählt.")
        self.print_button = Button("Drucken", on_click=self.print_document,
                                   variant="primary")
        self.close_button = Button("Schließen", on_click=self.close)
        self.layout = BoxLayout("vertical", spacing=6, padding=12)
        self.root.children.clear()
        self.layout.items.clear()
        for row in [
            HStack(Label("Profil"), self.profile, self.profile_name,
                   self.save_profile_button, self.load_profile_button),
            self.preview,
            HStack(Label("Papier"), self.paper),
            HStack(Label("Kopien"), self.copies),
            self.duplex, self.landscape,
            self.status,
            HStack(self.print_button, self.close_button),
        ]:
            self.root.add(row)
            self.layout.add(row)
        self._layout_root()
        self.invalidate()
        self._refresh_profiles()
        self._load_preview()

    def _refresh_profiles(self):
        self.profile.items = self.profile_store.names("print")
        if self.profile.items:
            self.profile.current_index = 0

    def _values(self):
        return {"paper": self.paper.current_text(),
                "copies": self.copies.text(),
                "duplex": self.duplex.checked,
                "landscape": self.landscape.checked}

    def save_profile(self):
        name = (self.profile_name.text().strip() or
                self.profile.current_text())
        if not name:
            self.status.text = "Kein Profilname vorhanden."
            self.invalidate()
            return
        self.profile_store.save("print", name, self._values())
        self.profile_name.set_text(name)
        self._refresh_profiles()
        self.status.text = f"Profil gespeichert: {name}"
        self.invalidate()

    def load_profile(self):
        name = self.profile.current_text()
        if not name:
            return
        try:
            values = self.profile_store.load("print", name)
        except Exception as error:
            self.status.text = f"Profilfehler: {error}"
            self.invalidate()
            return
        self.copies.set_text(values.get("copies", self.copies.text()))
        self.duplex.checked = bool(values.get("duplex", self.duplex.checked))
        self.landscape.checked = bool(values.get("landscape",
                                                 self.landscape.checked))
        paper = values.get("paper", self.paper.current_text())
        if paper in self.paper.items:
            self.paper.current_index = self.paper.items.index(paper)
        self.status.text = f"Profil geladen: {name}"
        self.invalidate()

    def _load_preview(self):
        if not self.pdf_path:
            return
        try:
            pages = render_pdf(self.pdf_path, dpi=100)
            self.preview.image = pages[0]
            self.preview._cache_key = None
            self.status.text = f"{len(pages)} Seite(n) · {Path(self.pdf_path).name}"
        except Exception as error:
            self.status.text = f"Vorschau nicht möglich: {error}"
        self.invalidate()

    def print_document(self):
        if not self.pdf_path:
            self.status.text = "Keine PDF gewählt."
            self.invalidate()
            return
        if not self.printer_name:
            self.status.text = "Kein Drucker gewählt."
            self.invalidate()
            return
        try:
            copies = max(1, int(self.copies.text() or "1"))
        except ValueError:
            self.status.text = "Ungültige Kopienzahl."
            self.invalidate()
            return
        try:
            print_pdf(self.pdf_path, self.printer_name, copies=copies,
                      duplex=self.duplex.checked,
                      paper=self.paper.current_text(),
                      landscape=self.landscape.checked)
        except Exception as error:
            self.status.text = f"Druckfehler: {error}"
        else:
            self.status.text = "Druckauftrag gesendet."
        self.invalidate()
