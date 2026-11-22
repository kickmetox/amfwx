"""SDL3 backend smoke test (dummy video driver)."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx.canvas import Canvas, Color
from amfwx.sdl3 import probe_sdl3
from amfwx.sdl3_backend import Sdl3Loop, Sdl3Renderer


@unittest.skipUnless(probe_sdl3().get("available"), "SDL3 nicht verfügbar")
class Sdl3BackendTests(unittest.TestCase):
    def test_present(self):
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        try:
            renderer = Sdl3Renderer(64, 48, "AMFWX Test")
            try:
                renderer.present(Canvas(64, 48, Color(200, 10, 20)))
                renderer.poll()
            finally:
                renderer.close()
        finally:
            os.environ.pop("SDL_VIDEODRIVER", None)

    def test_event_loop(self):
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        try:
            frames = []
            loop = Sdl3Loop(32, 24, "AMFWX Loop",
                            lambda w, h: Canvas(w, h, Color(1, 2, 3)))
            loop.step()
            frames.append(1)
            loop.run(max_frames=1)
            self.assertEqual(frames, [1])
        finally:
            os.environ.pop("SDL_VIDEODRIVER", None)

    def test_backend_info(self):
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        try:
            renderer = Sdl3Renderer(32, 24, "Backend")
            try:
                info = renderer.backend_info()
                self.assertEqual(info["video_driver"], "dummy")
                self.assertEqual(info["renderer"], "software")
                self.assertFalse(info["hardware"])
            finally:
                renderer.close()
        finally:
            os.environ.pop("SDL_VIDEODRIVER", None)


if __name__ == "__main__":
    unittest.main(verbosity=2)
