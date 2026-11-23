"""gPhoto2 adapter tests with a fake runner."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import GPhoto2Camera
from amfwx.gphoto2 import list_cameras


class Result:
    def __init__(self, stdout="", stderr="", returncode=0):
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode


class GPhoto2Tests(unittest.TestCase):
    def test_list(self):
        def runner(command, **kwargs):
            return Result("Model Port\nCanon EOS R5 usb:001,002\n")

        cameras = list_cameras(runner=runner)
        self.assertEqual(cameras[0]["model"], "Canon")
        self.assertEqual(cameras[0]["port"], "usb:001,002")

    def test_capture(self):
        calls = []

        def runner(command, **kwargs):
            calls.append(command)
            return Result()

        camera = GPhoto2Camera(runner=runner)
        with tempfile.TemporaryDirectory() as folder:
            path = camera.capture(folder, "shot.jpg")
            self.assertTrue(path.endswith("shot.jpg"))
            self.assertIn("--capture-image-and-download", calls[0])


if __name__ == "__main__":
    unittest.main(verbosity=2)
