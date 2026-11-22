"""Studio/scaffolding tests."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import ProjectError, Studio, StudioWindow


class StudioTests(unittest.TestCase):
    def test_create_templates(self):
        studio = Studio()
        self.assertIn("form", studio.templates())
        with tempfile.TemporaryDirectory() as folder:
            project = studio.create_project(folder, "demo", "form")
            self.assertEqual(project.files(),
                             [".gitignore", "README.md", "app.py"])
            self.assertIn("LineEdit", project.read())
            compile(project.read(), str(project.app), "exec")

    def test_invalid(self):
        studio = Studio()
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(ProjectError):
                studio.create_project(folder, "../bad", "blank")
            with self.assertRaises(ProjectError):
                studio.create_project(folder, "ok", "missing")

    def test_window(self):
        with tempfile.TemporaryDirectory() as folder:
            window = StudioWindow(projects_dir=folder)
            try:
                self.assertIsNotNone(window.panel)
                project = window._create("blank")
                self.assertTrue(project.app.exists())
            finally:
                window.close()
                window.process_events(40)


if __name__ == "__main__":
    unittest.main(verbosity=2)
