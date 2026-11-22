"""Advanced AMFWX widgets: tabs, tooltips, charts, property grid."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import Canvas, Color, Label, Rect
from amfwx.advanced import Chart, Property, PropertyGrid, TabView, Tooltip
from amfwx.widgets import Menu


class AdvancedWidgetTests(unittest.TestCase):
    def test_tabs(self):
        tabs = TabView()
        tabs.add_tab("A", Label("A"))
        tabs.add_tab("B", Label("B"))
        tabs.arrange(Rect(0, 0, 400, 240))
        canvas = Canvas(400, 240)
        tabs.paint(canvas)
        tabs.mouse_up(10, 10)
        self.assertEqual(tabs.active, 0)
        tabs.mouse_up(40, 10)
        self.assertEqual(tabs.active, 1)

    def test_chart(self):
        chart = Chart("Test")
        chart.add_series("A", [(0, 1), (1, 3), (2, 2)])
        chart.arrange(Rect(0, 0, 300, 200))
        canvas = Canvas(300, 200)
        chart.paint(canvas)
        self.assertTrue(any(canvas.pixel(x, 100) != Color(24, 26, 32)
                            for x in range(0, 300, 5)))

    def test_property_grid(self):
        changes = []
        grid = PropertyGrid([Property("size", "GrÃ¶ÃŸe", "int", 1)],
                            on_change=lambda name, value: changes.append(value))
        grid.arrange(Rect(0, 0, 300, 80))
        grid.editors["size"].set_text("5")
        self.assertEqual(grid.value("size"), 5)
        self.assertEqual(changes[-1], 5)

    def test_tooltip(self):
        tooltip = Tooltip("Hinweis")
        tooltip.arrange(Rect(0, 0, 100, 28))
        canvas = Canvas(120, 40)
        tooltip.paint(canvas)
        self.assertTrue(any(canvas.pixel(x, 10) != Color(24, 26, 32)
                            for x in range(0, 100, 4)))

    def test_context_menu(self):
        from amfwx import Label, Window
        window = Window("Context", 400, 300)
        label = Label("Rechtsklick")
        menu = Menu("Kontext")
        calls = []
        menu.add("Aktion", lambda: calls.append(1))
        label.context_menu = menu
        window.root.children.clear()
        window.root.add(label)
        label.arrange(Rect(10, 10, 200, 26))
        window._context_menu(label.rect.x + 4, label.rect.y + 4)
        self.assertIsNotNone(window.overlay)
        overlay = window.overlay
        overlay.mouse_up(overlay.rect.x + 10, overlay.rect.y + 10)
        self.assertEqual(calls, [1])
        window.close()
        window.process_events(40)

    def test_table_sort_and_resize(self):
        from amfwx import TableView
        table = TableView(["A", "B"], [["b", "1"], ["a", "2"]])
        table.arrange(Rect(0, 0, 300, 160))
        table.mouse_down(20, 10)
        self.assertEqual(table.rows[0][0], "a")
        table.mouse_down(20, 10)
        self.assertEqual(table.rows[0][0], "b")
        widths = table._widths()
        table.mouse_down(widths[0] - 1, 10)
        table.mouse_move(widths[0] + 20, 10)
        table.mouse_up(widths[0] + 20, 10)
        self.assertGreater(table._widths()[0], 100)

    def test_image_view(self):
        from amfwx import Canvas, Color, ImageView
        canvas = Canvas(8, 8, Color(200, 10, 20))
        view = ImageView(canvas)
        view.arrange(Rect(0, 0, 100, 100))
        output = Canvas(100, 100)
        view.paint(output)
        self.assertEqual(output.pixel(50, 50), Color(200, 10, 20))
        self.assertGreater(view.wheel(1), 1)

    def test_submenus(self):
        from amfwx import Label, Window
        from amfwx.widgets import Menu, MenuPopup
        window = Window("Submenu", 400, 300)
        menu = Menu("Datei")
        calls = []
        menu.add("Neu", lambda: calls.append("new"))
        submenu = menu.add_menu("Zuletzt")
        submenu.add("A", lambda: calls.append("a"))
        popup = MenuPopup(menu)
        popup.arrange(Rect(10, 10, 180, 60))
        window.set_overlay(popup)
        self.assertEqual(len(popup.entries()), 2)
        popup.mouse_up(20, 40)
        self.assertIsInstance(window.overlay, MenuPopup)
        window.overlay.mouse_up(20, 20)
        self.assertEqual(calls, ["a"])
        window.close()
        window.process_events(40)

    def test_status_and_tool_bar(self):
        from amfwx import StatusBar, ToolBar
        status = StatusBar(["A", "B"])
        status.arrange(Rect(0, 0, 200, 24))
        status.set_field(1, "C")
        status.paint(Canvas(200, 24))
        self.assertEqual(status.fields[1], "C")
        called = []
        toolbar = ToolBar([("X", lambda: called.append(1))])
        toolbar.arrange(Rect(0, 0, 200, 34))
        rect = toolbar._rects()[0]
        toolbar.mouse_move(rect.x + 2, rect.y + 2)
        toolbar.mouse_down(rect.x + 2, rect.y + 2)
        toolbar.mouse_up(rect.x + 2, rect.y + 2)
        self.assertEqual(called, [1])

    def test_splitter(self):
        from amfwx import Splitter
        splitter = Splitter()
        splitter.arrange(Rect(0, 0, 400, 200))
        divider = splitter._divider()
        splitter.mouse_down(divider.x + 1, divider.y + 1)
        splitter.mouse_move(300, 100)
        self.assertGreater(splitter.ratio, 0.5)
        splitter.mouse_up(300, 100)

    def test_tree_icons_and_keys(self):
        from amfwx import Color, TreeItem, TreeView
        child = TreeItem("Kind", icon=Color(10, 200, 10))
        root = TreeItem("Wurzel", [child], icon="▣")
        tree = TreeView([root])
        tree.arrange(Rect(0, 0, 300, 160))
        canvas = Canvas(300, 160)
        tree.paint(canvas)
        tree.selected = root
        tree.key_down(39, 0)
        self.assertTrue(root.expanded)
        tree.key_down(37, 0)
        self.assertFalse(root.expanded)
        tree.expand_all()
        self.assertTrue(root.expanded and child.expanded)
        tree.collapse_all()
        self.assertFalse(root.expanded)

    def test_software_shader(self):
        from amfwx import Shader, ShaderRenderer
        class Gradient(Shader):
            def fragment(self, varyings):
                return Color(int(255 * varyings[0]),
                             int(255 * varyings[1]), 0)
        canvas = Canvas(100, 100)
        renderer = ShaderRenderer(100, 100)
        renderer.render(
            canvas,
            [(-1, -1, 0), (1, -1, 0), (1, 1, 0), (-1, 1, 0)],
            [(0, 1, 2), (0, 2, 3)], Gradient(),
            __import__("amfwx").render3d.identity(),
            uvs=[(0, 0), (1, 0), (1, 1), (0, 1)])
        self.assertNotEqual(canvas.pixel(10, 10), canvas.pixel(90, 90))

    def test_table_multi_select(self):
        from amfwx import TableView
        table = TableView(["A"], [["1"], ["2"], ["3"]])
        table.multi_select = True
        selected = []
        table.on_select_many = lambda rows: selected.append(list(rows))
        table.arrange(Rect(0, 0, 200, 160))
        table.mouse_up(20, 40)
        table.mouse_up(20, 66)
        self.assertEqual(table.selected_rows, {0, 1})
        self.assertEqual(selected[-1], [0, 1])
        table.mouse_up(20, 40)
        self.assertEqual(table.selected_rows, {1})

    def test_tree_drag_drop(self):
        from amfwx import TreeItem, TreeView
        source = TreeItem("A")
        target = TreeItem("B")
        tree = TreeView([source, target])
        tree.arrange(Rect(0, 0, 300, 160))
        tree.mouse_down(40, 8)
        tree.mouse_move(40, 32)
        tree.mouse_up(40, 32)
        self.assertIn(source, target.children)
        self.assertNotIn(source, tree.items)

    def test_video_view(self):
        from amfwx import AviVideo, VideoView
        from tests.test_video import make_avi
        video = AviVideo(make_avi())
        view = VideoView(video)
        view.arrange(Rect(0, 0, 64, 64))
        canvas = Canvas(64, 64)
        view.paint(canvas)
        self.assertIsNotNone(view.player.frame())
        view.advance(0.1)
        view.pause()
        self.assertFalse(view.playing)

    def test_dock_manager(self):
        from amfwx import DockManager, Label
        central = Label("Zentral")
        dock = DockManager(central)
        left = dock.add_pane("Links", Label("L"), "left", 100)
        bottom = dock.add_pane("Unten", Label("B"), "bottom", 80)
        dock.arrange(Rect(0, 0, 400, 300))
        self.assertEqual(left.widget.rect.w, 100)
        self.assertEqual(bottom.widget.rect.h, 56)
        self.assertEqual(central.rect.x, 100)
        canvas = Canvas(400, 300)
        dock.paint(canvas)

    def test_dock_resize(self):
        from amfwx import DockManager, Label
        dock = DockManager(Label("C"))
        pane = dock.add_pane("L", Label("L"), "left", 100)
        dock.arrange(Rect(0, 0, 400, 300))
        dock.mouse_down(100, 100)
        dock.mouse_move(160, 100)
        dock.mouse_up(160, 100)
        self.assertEqual(pane.size, 160)
        self.assertEqual(dock.central.rect.x, 160)

    def test_dock_tabs(self):
        from amfwx import DockManager, Label
        dock = DockManager(Label("C"))
        pane = dock.add_pane("A", Label("A"), "left", 160)
        pane.add_tab("B", Label("B"))
        dock.arrange(Rect(0, 0, 400, 300))
        self.assertEqual(pane.title, "B")
        pane.select(0)
        self.assertEqual(pane.title, "A")
        canvas = Canvas(400, 300)
        dock.paint(canvas)
        dock.mouse_up(10, pane.widget.rect.y - 10)
        self.assertEqual(pane.active, 0)

    def test_dock_state(self):
        import tempfile
        from amfwx import DockManager, Label, Settings
        dock = DockManager(Label("C"))
        pane = dock.add_pane("A", Label("A"), "left", 140)
        dock.arrange(Rect(0, 0, 400, 300))
        with tempfile.TemporaryDirectory() as folder:
            settings = Settings(os.path.join(folder, "settings.json"))
            dock.save_state(settings)
            pane.size = 90
            dock.load_state(settings)
            self.assertEqual(pane.size, 140)

    def test_dock_float(self):
        from amfwx import DockManager, Label
        dock = DockManager(Label("C"))
        pane = dock.add_pane("L", Label("L"), "left", 100)
        dock.arrange(Rect(0, 0, 400, 300))
        window = dock.float_pane(pane)
        self.assertIsNotNone(window)
        self.assertEqual(len(dock.panes), 0)
        window.close()
        window.process_events(40)

    def test_dock_layout_presets(self):
        from amfwx import DockManager, Label
        dock = DockManager(Label("C"))
        pane = dock.add_pane("L", Label("L"), "left", 120)
        dock.arrange(Rect(0, 0, 400, 300))
        dock.save_layout("standard")
        pane.size = 200
        self.assertTrue(dock.apply_layout("standard"))
        self.assertEqual(pane.size, 120)

    def test_dock_presets_settings(self):
        import tempfile
        from amfwx import DockManager, Label, Settings
        dock = DockManager(Label("C"))
        dock.add_pane("L", Label("L"), "left", 120)
        dock.arrange(Rect(0, 0, 400, 300))
        dock.save_layout("standard")
        with tempfile.TemporaryDirectory() as folder:
            settings = Settings(os.path.join(folder, "settings.json"))
            dock.save_presets(settings)
            restored = DockManager(Label("C"))
            restored.add_pane("L", Label("L"), "left", 120)
            restored.load_presets(settings)
            self.assertIn("standard", restored.layouts)


if __name__ == "__main__":
    unittest.main(verbosity=2)

