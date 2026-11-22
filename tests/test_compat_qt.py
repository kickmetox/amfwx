"""Qt/PySide compatibility tests."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx.compat import qt


class QtCompatTests(unittest.TestCase):
    def test_window_layout_button(self):
        app = qt.QApplication([])
        window = qt.QMainWindow(title="Demo")
        central = qt.QWidget()
        layout = qt.QVBoxLayout(central)
        clicked = []
        button = qt.QPushButton("OK")
        button.clicked.connect(lambda: clicked.append(1))
        layout.addWidget(button)
        window.setCentralWidget(central)
        button.click()
        self.assertEqual(clicked, [1])
        window.close()

    def test_controls(self):
        app = qt.QApplication([])
        window = qt.QMainWindow(title="Controls")
        label = qt.QLabel("Hallo")
        label.setText("Neu")
        self.assertEqual(label.text(), "Neu")
        edit = qt.QLineEdit("a")
        edit.setText("b")
        self.assertEqual(edit.text(), "b")
        check = qt.QCheckBox("Aktiv")
        check.setChecked(True)
        self.assertTrue(check.isChecked())
        slider = qt.QSlider()
        slider.setValue(30)
        self.assertEqual(slider.value(), 30)
        combo = qt.QComboBox()
        combo.addItem("A")
        combo.addItem("B")
        combo.setCurrentIndex(1)
        self.assertEqual(combo.currentIndex(), 1)
        progress = qt.QProgressBar()
        progress.setValue(50)
        self.assertEqual(progress.widget.value(), 50)
        window.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
