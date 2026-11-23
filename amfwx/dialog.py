"""AMFWX dialogs and message boxes."""

from __future__ import annotations

from .window import Window
import glob
import os

from .canvas import Color, Rect
from .font import TrueTypeFont
from .widgets import BoxLayout, Button, ComboBox, Label, LineEdit, Widget


class Dialog(Window):
    def __init__(self, parent=None, title="Dialog", width=420, height=220):
        super().__init__(title, width, height,
                         theme=getattr(parent, "theme", None))
        self.parent_window = parent
        self.layout = BoxLayout(spacing=10, padding=16)
        self.root.children.clear()

    def add(self, widget, stretch=0):
        self.root.add(widget)
        self.layout.add(widget, stretch)
        self._layout_root()
        return widget

    def accept(self):
        self.close()


class MessageBox(Dialog):
    def __init__(self, parent=None, text="", title="AMFWX"):
        super().__init__(parent, title, 460, 190)
        self.add(Label(text, scale=2), 1)
        self.add(Button("OK", on_click=self.accept, variant="primary"), 0)

    @classmethod
    def show(cls, parent, text, title="AMFWX"):
        dialog = cls(parent, text, title)
        dialog.run()
        return dialog


class FindReplaceDialog(Dialog):
    def __init__(self, parent=None, title="Suchen und Ersetzen"):
        super().__init__(parent, title, 460, 240)
        self.find_input = LineEdit("")
        self.replace_input = LineEdit("")
        self.status = Label("", scale=1)
        self.add(Label("Suchen:", scale=1))
        self.add(self.find_input)
        self.add(Label("Ersetzen:", scale=1))
        self.add(self.replace_input)
        self.add(self.status)
        self.add(Button("Weiter", on_click=self.find_next))
        self.add(Button("Ersetzen", on_click=self.replace_current))
        self.add(Button("Alle ersetzen", on_click=self.replace_all))
        self.add(Button("Schließen", on_click=self.accept))

    def _editor(self):
        return getattr(self.parent_window, "editor", None)

    def find_next(self):
        editor = self._editor()
        if editor is None:
            return
        index = editor.find_next(self.find_input.text())
        self.status.text = ("gefunden" if index >= 0 else "nicht gefunden")
        self.invalidate()

    def replace_current(self):
        editor = self._editor()
        if editor is None:
            return
        needle = self.find_input.text()
        if editor.selected_text() == needle:
            editor.char_input(self.replace_input.text())
        else:
            self.find_next()

    def replace_all(self):
        editor = self._editor()
        if editor is None:
            return
        count = editor.replace_all(self.find_input.text(),
                                   self.replace_input.text())
        self.status.text = f"{count} ersetzt"
        self.invalidate()


class ColorSwatch(Widget):
    def __init__(self, color=None):
        super().__init__()
        self.color = color or Color(0, 0, 0)

    def size_hint(self):
        return (120, 40)

    def paint(self, canvas):
        theme = self.theme()
        canvas.fill_rect(self.rect, self.color)
        canvas.draw_rect(self.rect, theme.border, 1)


class ColorDialog(Dialog):
    def __init__(self, parent=None, color=None, title="Farbe"):
        super().__init__(parent, title, 360, 300)
        self.color = color or Color(0, 0, 0)
        self.result = None
        self.swatch = ColorSwatch(self.color)
        self.add(self.swatch)
        self.fields = {}
        for channel, value in (("R", self.color.r), ("G", self.color.g),
                               ("B", self.color.b)):
            self.add(Label(channel, scale=1))
            field = LineEdit(str(value))
            field.on_change = lambda _text: self._update()
            self.fields[channel] = field
            self.add(field)
        self.add(Button("OK", on_click=self.accept, variant="primary"))
        self.add(Button("Abbrechen", on_click=self.cancel))

    def _update(self):
        values = []
        for channel in ("R", "G", "B"):
            try:
                values.append(max(0, min(255, int(self.fields[channel].text()))))
            except ValueError:
                values.append(0)
        self.color = Color(*values)
        self.swatch.color = self.color
        self.invalidate()

    def accept(self):
        self._update()
        self.result = self.color
        self.close()

    def cancel(self):
        self.result = None
        self.close()

    @classmethod
    def pick(cls, parent=None, color=None):
        dialog = cls(parent, color)
        dialog.run()
        return dialog.result


class FontDialog(Dialog):
    def __init__(self, parent=None, font=None, title="Schrift"):
        super().__init__(parent, title, 420, 360)
        self.result = None
        self.font = font
        candidates = []
        for path in glob.glob(r"C:\Windows\Fonts\*.ttf"):
            name = os.path.basename(path)
            if any(key in name.lower() for key in
                   ("segoeui", "arial", "calibri", "times", "consola",
                    "verdana", "tahoma", "georgia")):
                candidates.append(path)
        candidates = sorted(candidates)[:12]
        self.fonts = candidates or [r"C:\Windows\Fonts\segoeui.ttf"]
        labels = [os.path.basename(path) for path in self.fonts]
        self.combo = ComboBox(labels, 0, on_change=lambda _index: self._update())
        self.add(Label("Schrift", scale=1))
        self.add(self.combo)
        self.size_input = LineEdit(str(getattr(font, "size", 18)))
        self.size_input.on_change = lambda _text: self._update()
        self.add(Label("Größe", scale=1))
        self.add(self.size_input)
        self.preview = Label("Aa Bb Cc 123", font=None)
        self.add(self.preview)
        self.add(Button("OK", on_click=self.accept, variant="primary"))
        self.add(Button("Abbrechen", on_click=self.cancel))
        self._update()

    def _update(self):
        try:
            size = max(6, min(96, int(self.size_input.text())))
        except ValueError:
            size = 18
        index = max(0, min(len(self.fonts) - 1, self.combo.current_index))
        try:
            self.font = TrueTypeFont(self.fonts[index], size)
        except Exception:
            return
        self.preview.font = self.font
        self.preview.text = "Aa Bb Cc 123 – " + os.path.basename(self.fonts[index])
        self.invalidate()

    def accept(self):
        self._update()
        self.result = self.font
        self.close()

    def cancel(self):
        self.result = None
        self.close()

    @classmethod
    def pick(cls, parent=None, font=None):
        dialog = cls(parent, font)
        dialog.run()
        return dialog.result

class CredentialsDialog(Dialog):
    """Username/password dialog for protected devices."""

    def __init__(self, parent=None, title="Zugangsdaten", username=""):
        super().__init__(parent, title, 420, 260)
        self.result = None
        self.username = LineEdit(str(username))
        self.password = LineEdit("", password=True)
        self.add(Label("Benutzername", scale=1))
        self.add(self.username)
        self.add(Label("Passwort", scale=1))
        self.add(self.password)
        self.add(Button("OK", on_click=self.accept, variant="primary"))
        self.add(Button("Abbrechen", on_click=self.cancel))

    def accept(self):
        self.result = {"username": self.username.text(),
                       "password": self.password.text()}
        self.close()

    def cancel(self):
        self.result = None
        self.close()

    @classmethod
    def ask(cls, parent=None, title="Zugangsdaten", username=""):
        dialog = cls(parent, title, username)
        dialog.run()
        return dialog.result

