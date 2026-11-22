"""AMFWX text layout, editor, clipboard, IME and DPI."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import (
    Canvas, Color, TextEdit, TextLayout, Window, bidi_reorder,
    get_clipboard_files, get_clipboard_html, get_clipboard_image,
    get_clipboard_text,
    set_clipboard_files, set_clipboard_html, set_clipboard_image,
    set_clipboard_text,
)
from amfwx.font import TrueTypeFont
from amfwx.widgets import Label


class TextInputTests(unittest.TestCase):
    def test_word_wrap(self):
        path = r"C:\Windows\Fonts\segoeui.ttf"
        if not os.path.exists(path):
            self.skipTest("Segoe UI fehlt")
        font = TrueTypeFont(path, 16)
        layout = TextLayout(font, max_width=80)
        lines = layout.lines("Dies ist ein langer Text mit Umbruch")
        self.assertGreater(len(lines), 1)
        self.assertLessEqual(max(line.width for line in lines), 90)

    def test_textedit_keys(self):
        editor = TextEdit("ab\ncd")
        editor.cursor = 2
        editor.anchor = 2
        editor.key_down(8)
        self.assertEqual(editor.text(), "a\ncd")
        editor.char_input("X")
        self.assertEqual(editor.text(), "aX\ncd")
        editor.key_down(13)
        self.assertEqual(editor.text(), "aX\n\ncd")

    def test_clipboard_roundtrip(self):
        set_clipboard_text("AMFWX Clip")
        self.assertEqual(get_clipboard_text(), "AMFWX Clip")

    def test_ime_hooks_and_dpi(self):
        window = Window("ime", 300, 200)
        label = Label("ime")
        label.arrange(type("R", (), {"x": 0, "y": 0, "w": 100,
                                     "h": 30})())
        window.root.children.clear()
        window.root.add(label)
        window.set_focus(label)
        window._ime_start()
        window._ime_composition(0x8)
        window._ime_end()
        self.assertGreaterEqual(window.dpi, 96)
        self.assertGreaterEqual(window.dpi_scale, 1.0)
        window.close()
        window.process_events(40)

    def test_layout_draw(self):
        canvas = Canvas(200, 80, Color(0, 0, 0))
        path = r"C:\Windows\Fonts\segoeui.ttf"
        if not os.path.exists(path):
            self.skipTest("Segoe UI fehlt")
        layout = TextLayout(TrueTypeFont(path, 18), max_width=120)
        layout.draw(canvas, "Hallo Welt", 4, 4)
        self.assertTrue(any(canvas.pixel(x, y) != Color(0, 0, 0)
                            for x in range(0, 100, 4) for y in range(0, 40, 2)))

    def test_rich_clipboard_and_bidi(self):
        set_clipboard_html("<b>Hallo</b>", "Hallo")
        self.assertEqual(get_clipboard_html(), "<b>Hallo</b>")
        self.assertEqual(get_clipboard_text(), "Hallo")
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False) as handle:
            path = handle.name
        try:
            set_clipboard_files([path])
            self.assertEqual(get_clipboard_files(), [path])
        finally:
            os.unlink(path)
        self.assertNotEqual(bidi_reorder("مرحبا hello"), "مرحبا hello")

    def test_textedit_selection_undo_clipboard(self):
        editor = TextEdit("abcdef")
        editor.cursor = 1
        editor.anchor = 1
        editor.key_down(39, 1)  # shift-right
        self.assertEqual(editor.selected_text(), "b")
        editor.key_down(67, 2)  # ctrl-c
        self.assertEqual(get_clipboard_text(), "b")
        editor.key_down(90, 2)  # ctrl-z? no snapshot yet
        editor.char_input("X")
        editor.key_down(90, 2)
        self.assertEqual(editor.text(), "abcdef")
        editor.key_down(89, 2)
        self.assertEqual(editor.text(), "aXcdef")

    def test_clipboard_image(self):
        from amfwx import Canvas, Color
        image = Canvas(4, 3, Color(10, 20, 30))
        self.assertTrue(set_clipboard_image(image))
        restored = get_clipboard_image()
        self.assertIsNotNone(restored)
        self.assertEqual((restored.width, restored.height), (4, 3))
        self.assertEqual(restored.pixel(2, 1), Color(10, 20, 30))

    def test_find_replace(self):
        from amfwx import FindReplaceDialog, Window
        window = Window("Find", 400, 300)
        editor = TextEdit("eins zwei eins")
        window.root.add(editor)
        window.editor = editor
        dialog = FindReplaceDialog(window)
        dialog.find_input.set_text("eins")
        dialog.find_next()
        self.assertEqual(editor.selected_text(), "eins")
        dialog.replace_input.set_text("drei")
        dialog.replace_all()
        self.assertEqual(editor.text(), "drei zwei drei")
        window.close()
        window.process_events(40)

    def test_color_dialog(self):
        from amfwx import Color, ColorDialog, Window
        window = Window("Color", 300, 200)
        dialog = ColorDialog(window, Color(1, 2, 3))
        dialog.fields["R"].set_text("255")
        dialog.fields["G"].set_text("10")
        dialog.fields["B"].set_text("20")
        dialog._update()
        self.assertEqual(dialog.color, Color(255, 10, 20))
        dialog.close()
        window.close()
        window.process_events(40)

    def test_font_dialog(self):
        from amfwx import FontDialog, Window
        window = Window("Font", 400, 300)
        dialog = FontDialog(window)
        self.assertTrue(dialog.fonts)
        dialog.size_input.set_text("24")
        dialog._update()
        self.assertEqual(dialog.font.size, 24)
        dialog.close()
        window.close()
        window.process_events(40)

    def test_canvas_scale_crop(self):
        from amfwx import Canvas, Color
        canvas = Canvas(4, 4, Color(100, 50, 20))
        scaled = canvas.scaled(8, 6)
        self.assertEqual((scaled.width, scaled.height), (8, 6))
        self.assertEqual(scaled.pixel(3, 3), Color(100, 50, 20))
        crop = canvas.crop(1, 1, 2, 2)
        self.assertEqual((crop.width, crop.height), (2, 2))
        self.assertEqual(canvas.thumbnail(2).width, 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
