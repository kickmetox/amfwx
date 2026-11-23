"""Small GUI for eSCL scans to folder/PDF."""

from __future__ import annotations

import threading
import time
from pathlib import Path

from .escl import EsclScanner
from .scan_pdf import scan_to_pdf
from .scan_transfer import default_scan_dir, scan_to_folder
from .quick import HStack
from .widgets import BoxLayout, Button, CheckBox, Label, LineEdit
from .window import Window


class ScanWindow(Window):
    def __init__(self):
        super().__init__("AMFWX Scan", 700, 430)
        self.host = LineEdit("", placeholder="192.168.178.93")
        self.port = LineEdit("9096")
        self.source = LineEdit("Platen")
        self.pages = LineEdit("1")
        self.folder = LineEdit(str(default_scan_dir()))
        self.pdf = CheckBox("Als PDF speichern", checked=False)
        self.http = CheckBox("HTTP statt HTTPS", checked=False)
        self.status = Label("Bereit.")
        self.scan_button = Button("Scannen", on_click=self.scan,
                                  variant="primary")
        self.close_button = Button("Schließen", on_click=self.close)
        self.layout = BoxLayout("vertical", spacing=6, padding=12)
        self.root.children.clear()
        self.layout.items.clear()
        rows = [
            HStack(Label("Host"), self.host),
            HStack(Label("Port"), self.port),
            HStack(Label("Quelle"), self.source),
            HStack(Label("Seiten"), self.pages),
            HStack(Label("Ordner"), self.folder),
            self.pdf,
            self.http,
            self.status,
            HStack(self.scan_button, self.close_button),
        ]
        for row in rows:
            self.root.add(row)
            self.layout.add(row)
        self._layout_root()
        self.invalidate()

    def scan(self):
        self.scan_button.enabled = False
        self.status.text = "Scan läuft..."
        self.invalidate()
        try:
            host = self.host.text().strip()
            port = int(self.port.text() or "9096")
            source = self.source.text().strip() or "Platen"
            pages = max(1, int(self.pages.text() or "1"))
            folder = Path(self.folder.text().strip() or default_scan_dir())
            use_pdf = self.pdf.checked
            secure = not self.http.checked
        except ValueError as error:
            self.status.text = f"Eingabefehler: {error}"
            self.scan_button.enabled = True
            self.invalidate()
            return
        if not host:
            self.status.text = "Host fehlt."
            self.scan_button.enabled = True
            self.invalidate()
            return

        def work():
            try:
                scanner = EsclScanner(host, port, secure=secure,
                                      timeout=90)
                if use_pdf:
                    target = folder / f"scan_{time.strftime('%Y%m%d_%H%M%S')}.pdf"
                    files = [scan_to_pdf(scanner, target, source=source,
                                         max_pages=pages)]
                else:
                    target = folder / f"scan_{time.strftime('%Y%m%d_%H%M%S')}.jpg"
                    files = scan_to_folder(scanner, folder,
                                           prefix=target.stem,
                                           source=source,
                                           max_pages=pages)
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
