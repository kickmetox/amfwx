"""Optional AMFW + AMFWX bridge test."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, r"D:\AI_Temp\AMFW")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from amfw import Application, Label as AMFWLabel, Window
    from amfw.core.event import MouseEvent
    from amfwx import BoxLayout, Button, Label, Panel
    from amfwx.amfw_bridge import AmfwxView, AmfwxWindowHost
except Exception:
    Application = None


@unittest.skipIf(Application is None, "AMFW not available")
class BridgeTests(unittest.TestCase):
    def test_host_amfwx_in_amfw(self):
        app = Application.instance() if Application.has_instance() else Application(
            theme="dark", auto_theme=False)
        window = Window("Bridge", 640, 420)
        root = Panel()
        root.layout = BoxLayout(spacing=8, padding=12)
        hits = []
        button = Button("Bridge", on_click=lambda: hits.append(1))
        root.layout.add(Label("AMFWX", scale=3))
        root.layout.add(button)
        for item, _stretch in root.layout.items:
            root.add(item)
        view = AmfwxView(root, 420, 220)
        window.set_central_widget(view)
        window.show()
        try:
            app.process_events(40)
            view.mouse_press_event(MouseEvent(x=int(button.rect.x + 4),
                                              y=int(button.rect.y + 4)))
            view.mouse_release_event(MouseEvent(x=int(button.rect.x + 4),
                                                y=int(button.rect.y + 4)))
            self.assertEqual(hits, [1])
            self.assertGreater(window.render_to_image().width, 100)
        finally:
            window.close()
            app.process_events(20)


    def test_amfw_window_embedded_in_amfwx(self):
        import ctypes
        app = Application.instance() if Application.has_instance() else Application(
            theme="dark", auto_theme=False)
        child = Window("AMFW child", 300, 200)
        child.set_central_widget(AMFWLabel("child"))
        child.show()
        app.process_events(30)
        host_window = __import__("amfwx").Window("host", 600, 400)
        try:
            AmfwxWindowHost(child).attach(host_window)
            app.process_events(50)
            user32 = ctypes.WinDLL("user32")
            user32.GetParent.argtypes = [ctypes.c_void_p]
            user32.GetParent.restype = ctypes.c_void_p
            self.assertEqual(int(user32.GetParent(child.hwnd) or 0),
                             int(host_window.hwnd))
        finally:
            host_window.close()
            app.process_events(30)


if __name__ == "__main__":
    unittest.main(verbosity=2)
