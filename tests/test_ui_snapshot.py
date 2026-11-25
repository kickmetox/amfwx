"""Screenshot baseline regression test."""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.ui_snapshot import digest, snapshot
from amfwx import Window


@unittest.skipUnless(sys.version_info[:2] == (3, 12),
                     "Pixel-Baseline ist an Python 3.12 gebunden")
class SnapshotTests(unittest.TestCase):
    def test_snapshot_matches_baseline(self):
        baseline = ROOT / "tests" / "baselines" / "snapshot.json"
        expected = json.loads(baseline.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as folder:
            for theme, wanted in expected.items():
                path = Path(folder) / f"snapshot_{theme}.png"
                snapshot(path, theme)
                self.assertEqual(digest(path), wanted, theme)

    def test_scaled_render(self):
        from amfwx import Canvas
        window = Window("Scale", 200, 120)
        try:
            with tempfile.TemporaryDirectory() as folder:
                path = Path(folder) / "scale.png"
                window.render_to_png(path, scale=2)
                image = Canvas.from_png(path)
                self.assertEqual((image.width, image.height), (400, 240))
        finally:
            window.close()
            window.process_events(40)


if __name__ == "__main__":
    unittest.main(verbosity=2)
