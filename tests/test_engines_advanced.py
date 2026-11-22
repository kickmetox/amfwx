"""AMFWX advanced engines: TTF composites, camera, UIA tree, SDL probe."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import (
    Camera, Canvas, CheckBox, Color, Label, Slider, SoftwareRenderer, TableView,
    TextEdit, Texture, TreeItem, TreeView, Window, clip_near, cube,
    probe_sdl3, tree_from_window,
)
from amfwx.font import TrueTypeFont
from amfwx.uia_provider import (
    UIA_ExpandCollapsePatternId, UIA_NamePropertyId, UIA_RangeValuePatternId,
    UIA_GridPatternId, UIA_SelectionPatternId, UIA_TogglePatternId,
    UIA_ValuePatternId,
    UiaProvider, VARIANT,
)
from amfwx.uia_text import UIA_TextPatternId


class AdvancedEngineTests(unittest.TestCase):
    def test_ttf_kerning_and_composite(self):
        path = r"C:\Windows\Fonts\segoeui.ttf"
        if not os.path.exists(path):
            self.skipTest("Segoe UI fehlt")
        font = TrueTypeFont(path, 24)
        self.assertGreater(len(font.kern), 0)
        self.assertGreater(len(font.cmap), 100)
        self.assertTrue(font._outline(font.glyph_id("Ä")))
        self.assertLessEqual(len(font.shape("fi")), 2)
        self.assertGreater(len(font.gpos_pairs), 0)
        self.assertNotEqual(font.kerning(font.glyph_id("A"),
                                         font.glyph_id("V")), 0)
        positioned = font.positioned("a\u0301")
        self.assertTrue(any(dx or dy for _gid, dx, dy in positioned))
        mark_mark = font.positioned("a\u0301\u0302")
        self.assertTrue(any(dx or dy for _gid, dx, dy in mark_mark[2:]))
        self.assertGreater(len(font.mark_ligature_positions), 0)

    def test_camera_and_near_clip(self):
        camera = Camera((0, 0, 3), (0, 0, 0), aspect=1.2)
        matrix = camera.matrix()
        self.assertEqual(len(matrix), 4)
        polygon = [(-1, -1, -2), (1, -1, -2), (1, 1, -2), (-1, 1, 0.5)]
        clipped = clip_near(polygon, 0.1)
        self.assertLessEqual(max(point[2] for point in clipped), -0.09)
        canvas = Canvas(100, 100)
        SoftwareRenderer(100, 100).render(canvas, cube(1.0), matrix)
        self.assertTrue(any(canvas.pixel(x, 50) != Color(20, 22, 28)
                            for x in range(100)))

    def test_uia_tree(self):
        window = Window("UIA", 400, 300)
        window.root.children.clear()
        window.root.add(Label("Name"))
        tree = tree_from_window(window)
        self.assertEqual(tree.role, "Window")
        self.assertTrue(tree.children)
        self.assertIn("children", tree.as_dict())
        window.close()
        window.process_events(40)

    def test_sdl_probe(self):
        result = probe_sdl3()
        self.assertIn("available", result)
        self.assertIn("features", result)

    def test_uia_com_provider(self):
        import ctypes
        window = Window("UIA Provider", 400, 300)
        window.root.children.clear()
        window.root.add(Label("Name"))
        provider = UiaProvider(window)
        self.assertGreater(len(provider.root.children), 0)
        value = VARIANT()
        provider.root._property(provider.root.simple, UIA_NamePropertyId,
                                ctypes.pointer(value))
        self.assertTrue(value.vt)
        window.enable_uia()
        self.assertIsNotNone(window._uia_getobject())
        window.close()
        window.process_events(40)

    def test_uia_value_pattern(self):
        import ctypes
        from amfwx import LineEdit
        window = Window("UIA Value", 400, 300)
        edit = LineEdit("alt")
        window.root.children.clear()
        window.root.add(edit)
        provider = UiaProvider(window)
        window.uia_provider = provider
        child = provider.root.children[0]
        pattern = ctypes.c_void_p()
        child._pattern(child.simple, UIA_ValuePatternId, ctypes.pointer(pattern))
        self.assertIsNotNone(pattern.value)
        text = ctypes.c_void_p()
        child._get_value(child.simple, ctypes.pointer(text))
        self.assertTrue(text.value)
        child._set_value(child.simple, "neu")
        self.assertEqual(edit.text(), "neu")
        provider.raise_event(20005, child)
        window.close()
        window.process_events(40)

    def test_uia_text_pattern(self):
        import ctypes
        window = Window("UIA Text", 400, 300)
        edit = TextEdit("Hallo Welt")
        window.root.children.clear()
        window.root.add(edit)
        provider = UiaProvider(window)
        child = provider.root.children[0]
        pattern = ctypes.c_void_p()
        child._pattern(child.simple, UIA_TextPatternId, ctypes.pointer(pattern))
        self.assertIsNotNone(pattern.value)
        text_provider = child.text_provider
        range_pointer = ctypes.c_void_p()
        text_provider._document(text_provider.simple,
                                ctypes.pointer(range_pointer))
        self.assertTrue(range_pointer.value)
        text_range = [item for item in child.ranges
                      if item.simple.value == range_pointer.value][0]
        buffer = ctypes.c_void_p()
        text_range._get_text(text_range.simple, 100, ctypes.pointer(buffer))
        self.assertEqual(ctypes.wstring_at(buffer.value), "Hallo Welt")
        window.close()
        window.process_events(40)

    def test_texture_and_selection_pattern(self):
        import ctypes
        texture = Texture(2, 2, bytes((0, 0, 255, 255) * 4))
        canvas = Canvas(80, 80, Color(0, 0, 0))
        SoftwareRenderer(80, 80).render(canvas, cube(1.5), Camera(
            (0, 0, 3), (0, 0, 0), aspect=1.0).matrix(), texture=texture)
        self.assertTrue(any(canvas.pixel(x, 40) != Color(0, 0, 0)
                            for x in range(80)))
        window = Window("selection", 400, 300)
        table = TableView(["A"], [["x"]])
        table.selected = 0
        window.root.children.clear()
        window.root.add(table)
        provider = UiaProvider(window)
        child = provider.root.children[0]
        self.assertGreater(len(child.children), 0)
        pattern = ctypes.c_void_p()
        child._pattern(child.simple, UIA_SelectionPatternId,
                       ctypes.pointer(pattern))
        self.assertIsNotNone(pattern.value)
        array = ctypes.c_void_p()
        child._get_selection(child.simple, ctypes.pointer(array))
        self.assertIsNotNone(array.value)
        window.close()
        window.process_events(40)

    def test_uia_tree_nodes(self):
        import ctypes
        from amfwx.uia_provider import UIA_SelectionPatternId
        window = Window("UIA Tree", 400, 300)
        child = TreeItem("Child")
        tree = TreeView([TreeItem("Root", [child])])
        tree.selected = child
        window.root.children.clear()
        window.root.add(tree)
        provider = UiaProvider(window)
        node = provider.root.children[0]
        self.assertEqual(len(node.children), 2)
        pattern = ctypes.c_void_p()
        node._pattern(node.simple, UIA_SelectionPatternId,
                      ctypes.pointer(pattern))
        self.assertIsNotNone(pattern.value)
        array = ctypes.c_void_p()
        node._get_selection(node.simple, ctypes.pointer(array))
        self.assertIsNotNone(array.value)
        window.close()
        window.process_events(40)

    def test_uia_expand_collapse(self):
        import ctypes
        window = Window("UIA Expand", 400, 300)
        child = TreeItem("Child")
        root_item = TreeItem("Root", [child])
        tree = TreeView([root_item])
        window.root.children.clear()
        window.root.add(tree)
        provider = UiaProvider(window)
        node = provider.root.children[0]
        root_provider = node.children[0]
        pattern = ctypes.c_void_p()
        root_provider._pattern(root_provider.simple,
                               UIA_ExpandCollapsePatternId,
                               ctypes.pointer(pattern))
        self.assertIsNotNone(pattern.value)
        root_provider._collapse(root_provider.simple)
        self.assertFalse(root_item.expanded)
        state = ctypes.c_int()
        root_provider._expand_state(root_provider.simple,
                                    ctypes.pointer(state))
        self.assertEqual(state.value, 0)
        root_provider._expand(root_provider.simple)
        self.assertTrue(root_item.expanded)
        window.close()
        window.process_events(40)

    def test_uia_textrange_operations(self):
        import ctypes
        window = Window("UIA Range", 400, 300)
        edit = TextEdit("eins zwei drei")
        window.root.children.clear()
        window.root.add(edit)
        provider = UiaProvider(window)
        child = provider.root.children[0]
        text_provider = child.text_provider
        pointer = ctypes.c_void_p()
        text_provider._document(text_provider.simple, ctypes.pointer(pointer))
        text_range = [item for item in child.ranges
                      if item.simple.value == pointer.value][0]
        text_range.start = text_range.end = 0
        moved = ctypes.c_int()
        text_range._move(text_range.simple, 2, 1, ctypes.pointer(moved))
        self.assertGreater(text_range.start, 0)
        found = ctypes.c_void_p()
        text_range._find_text(text_range.simple, "drei", False, False,
                              ctypes.pointer(found))
        self.assertTrue(found.value)
        rects = ctypes.c_void_p()
        text_range._rectangles(text_range.simple, ctypes.pointer(rects))
        self.assertTrue(rects.value)
        window.close()
        window.process_events(40)

    def test_uia_range_value(self):
        import ctypes
        window = Window("UIA Range", 400, 300)
        slider = Slider(0, 100, 10)
        window.root.children.clear()
        window.root.add(slider)
        provider = UiaProvider(window)
        child = provider.root.children[0]
        pattern = ctypes.c_void_p()
        child._pattern(child.simple, UIA_RangeValuePatternId,
                       ctypes.pointer(pattern))
        self.assertIsNotNone(pattern.value)
        child._range_set(child.simple, 42.0)
        value = ctypes.c_double()
        child._range_value(child.simple, ctypes.pointer(value))
        self.assertEqual(value.value, 42.0)
        window.close()
        window.process_events(40)

    def test_uia_toggle(self):
        import ctypes
        window = Window("UIA Toggle", 400, 300)
        check = CheckBox("aktiv", False)
        window.root.children.clear()
        window.root.add(check)
        provider = UiaProvider(window)
        child = provider.root.children[0]
        pattern = ctypes.c_void_p()
        child._pattern(child.simple, UIA_TogglePatternId,
                       ctypes.pointer(pattern))
        self.assertIsNotNone(pattern.value)
        state = ctypes.c_int()
        child._toggle_state(child.simple, ctypes.pointer(state))
        self.assertEqual(state.value, 0)
        child._toggle(child.simple)
        child._toggle_state(child.simple, ctypes.pointer(state))
        self.assertEqual(state.value, 1)
        window.close()
        window.process_events(40)

    def test_uia_grid_pattern(self):
        import ctypes
        window = Window("Grid", 400, 300)
        table = TableView(["A", "B"], [["1", "2"], ["3", "4"]])
        window.root.children.clear()
        window.root.add(table)
        provider = UiaProvider(window)
        node = provider.root.children[0]
        self.assertEqual(len(node.children), 2)
        pattern = ctypes.c_void_p()
        node._pattern(node.simple, UIA_GridPatternId,
                      ctypes.pointer(pattern))
        self.assertIsNotNone(pattern.value)
        rows = ctypes.c_int()
        columns = ctypes.c_int()
        node._grid_rows(node.simple, ctypes.pointer(rows))
        node._grid_columns(node.simple, ctypes.pointer(columns))
        self.assertEqual((rows.value, columns.value), (2, 2))
        cell = ctypes.c_void_p()
        node._grid_item(node.simple, 1, 1, ctypes.pointer(cell))
        self.assertTrue(cell.value)
        window.close()
        window.process_events(40)

    def test_normal_mapping(self):
        texture = Texture(2, 2, bytes((0, 0, 255, 255) * 4))
        normal_map = Texture(2, 2, bytes((128, 128, 255, 255) * 4))
        canvas = Canvas(80, 80, Color(0, 0, 0))
        SoftwareRenderer(80, 80).render(
            canvas, cube(1.5),
            Camera((0, 0, 3), (0, 0, 0), aspect=1.0).matrix(),
            texture=texture, normal_map=normal_map)
        self.assertTrue(any(canvas.pixel(x, 40) != Color(0, 0, 0)
                            for x in range(80)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
