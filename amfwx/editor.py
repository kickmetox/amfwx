"""A small real AMFWX editor application."""

from __future__ import annotations

import os
from pathlib import Path

from .advanced import Tooltip
from .clipboard import get_text, set_text
from .dialog import MessageBox
from .filedialog import open_file, save_file
from .settings import Settings
from .textedit import TextEdit
from .widgets import BoxLayout, Label, MenuBar
from .window import Window


class EditorWindow(Window):
    def __init__(self, path=None):
        super().__init__("AMFWX Editor", 900, 620)
        self.path = str(path) if path else ""
        self.dirty = False
        self.settings = Settings()
        self.load_geometry(self.settings)
        menu = MenuBar()
        file_menu = menu.add_menu("Datei")
        file_menu.add("Neu", self.new_file, "Ctrl+N")
        file_menu.add("Ã–ffnen", self.open_file, "Ctrl+O")
        file_menu.add("Speichern", self.save_file, "Ctrl+S")
        file_menu.add("Speichern unter", self.save_as, "Ctrl+Shift+S")
        file_menu.add("Beenden", self.close, "Ctrl+Q")
        edit_menu = menu.add_menu("Bearbeiten")
        self.recent_menu = menu.add_menu("Zuletzt")
        edit_menu.add("RÃ¼ckgÃ¤ngig", lambda: self.editor.undo(), "Ctrl+Z")
        edit_menu.add("Wiederholen", lambda: self.editor.redo(), "Ctrl+Y")
        edit_menu.add("Alles auswählen", lambda: self.editor.select_all(), "Ctrl+A")
        edit_menu.add("Kopieren", self.copy, "Ctrl+C")
        edit_menu.add("EinfÃ¼gen", self.paste, "Ctrl+V")
        self.layout = BoxLayout(spacing=6, padding=8)
        self.root.children.clear()
        self.root.add(menu)
        self.layout.add(menu)
        self.editor = TextEdit("", on_change=self._changed)
        self.root.add(self.editor)
        self.layout.add(self.editor, 1)
        self.status = Label("Bereit", scale=1)
        self.status.tooltip_text = "Status"
        self.root.add(self.status)
        self.layout.add(self.status)
        self._layout_root()
        self._rebuild_recent()
        if path and Path(path).exists():
            self.load(path)

    def close(self):
        try:
            self.save_geometry(self.settings)
        except Exception:
            pass
        super().close()

    def _changed(self, _text):
        self.dirty = True
        self._update_title()

    def _update_title(self):
        name = Path(self.path).name if self.path else "Unbenannt"
        marker = "*" if self.dirty else ""
        self.title = f"{name}{marker} â€“ AMFWX Editor"

    def load(self, path):
        try:
            text = Path(path).read_text(encoding="utf-8")
        except OSError as error:
            MessageBox.show(self, str(error))
            return False
        self.path = str(path)
        self.settings.add_recent(self.path)
        self._rebuild_recent()
        self.editor.set_text(text)
        self.dirty = False
        self._update_title()
        self.invalidate()
        return True

    def new_file(self):
        self.path = ""
        self.editor.set_text("")
        self.dirty = False
        self._update_title()

    def open_file(self):
        path = open_file(self, "Ã–ffnen", "Textdateien (*.txt *.md)|*.txt;*.md|Alle Dateien (*.*)|*.*")
        if path:
            self.load(path)

    def save_file(self):
        if not self.path:
            return self.save_as()
        try:
            Path(self.path).write_text(self.editor.text(), encoding="utf-8")
        except OSError as error:
            MessageBox.show(self, str(error))
            return False
        self.dirty = False
        self.settings.add_recent(self.path)
        self._rebuild_recent()
        self._update_title()
        return True

    def save_as(self):
        path = save_file(self, "Speichern unter", "Textdateien (*.txt)|*.txt|Alle Dateien (*.*)|*.*")
        if not path:
            return False
        self.path = path
        return self.save_file()

    def _rebuild_recent(self):
        if not hasattr(self, "recent_menu"):
            return
        self.recent_menu.actions.clear()
        paths = self.settings.recent()
        if not paths:
            self.recent_menu.add("(leer)")
            return
        for path in paths[:8]:
            self.recent_menu.add(Path(path).name,
                                 lambda item=path: self.load(item))

    def find_replace(self):
        from .dialog import FindReplaceDialog
        self.find_dialog = FindReplaceDialog(self)
        self.find_dialog.run()

    def copy(self):
        if self.editor.has_selection():
            set_text(self.editor.selected_text())

    def paste(self):
        text = get_text()
        if text:
            self.editor.char_input(text)


def main():
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else None
    return EditorWindow(path).run()

