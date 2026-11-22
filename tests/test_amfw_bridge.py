"""Optional AMFW/AMFWX bridge integration tests."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import amfw
    HAS_AMFW = True
except Exception:
    amfw = None
    HAS_AMFW = False


@unittest.skipUnless(HAS_AMFW, "AMFW nicht installiert")
class BridgeTests(unittest.TestCase):
    def test_amfwx_view_canvas(self):
        from amfwx import Label
        from amfwx.amfw_bridge import AmfwxView

        view = AmfwxView(Label("Bridge"), 200, 80)
        canvas = view._canvas()
        self.assertEqual((canvas.width, canvas.height), (200, 80))
        self.assertEqual(view.size_hint(), (200, 80))

    def test_amfw_window_host(self):
        if not amfw.Application.has_instance():
            amfw.Application()
        from amfwx import Window
        from amfwx.amfw_bridge import AmfwxWindowHost

        host = Window("AMFWX Bridge Host", 400, 300)
        child = amfw.Window("AMFW Child", 300, 200)
        try:
            bridge = AmfwxWindowHost(child).attach(host)
            self.assertIsNotNone(bridge.host_hwnd)
            bridge.resize(0, 0, 300, 200)
        finally:
            child.close()
            host.close()
            host.process_events(40)


if __name__ == "__main__":
    unittest.main(verbosity=2)
