"""Credentials dialog and password field tests."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import CredentialsDialog
from amfwx.widgets import LineEdit


class CredentialsTests(unittest.TestCase):
    def test_password_field(self):
        field = LineEdit("secret", password=True)
        self.assertTrue(field.password)
        self.assertEqual(field.text(), "secret")

    def test_dialog(self):
        dialog = CredentialsDialog(username="user")
        try:
            dialog.password.set_text("pass")
            dialog.accept()
            self.assertEqual(dialog.result,
                             {"username": "user", "password": "pass"})
        finally:
            dialog.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
