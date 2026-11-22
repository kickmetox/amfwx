"""Form validation tests."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import (Field, Form, LineEdit, ValidationError, email, integer,
                   max_length, min_length, number_range, pattern, required)


class ValidationTests(unittest.TestCase):
    def test_form(self):
        form = Form()
        form.add("name", LineEdit(""), [required, min_length(3)])
        form.add("mail", LineEdit("a@b.de"), [email])
        self.assertFalse(form.validate())
        self.assertIn("name", form.errors())
        form.fields[0].widget.set_text("Ada")
        self.assertTrue(form.validate())

    def test_validators(self):
        with self.assertRaises(ValidationError):
            required("")
        with self.assertRaises(ValidationError):
            min_length(3)("ab")
        with self.assertRaises(ValidationError):
            max_length(3)("abcd")
        with self.assertRaises(ValidationError):
            pattern(r"[0-9]+")("abc")
        with self.assertRaises(ValidationError):
            email("nope")
        with self.assertRaises(ValidationError):
            integer("x")
        self.assertEqual(number_range(0, 10)("5"), 5.0)

    def test_field_values(self):
        field = Field("x", LineEdit("abc"))
        self.assertEqual(field.value(), "abc")
        self.assertTrue(field.validate())


if __name__ == "__main__":
    unittest.main(verbosity=2)
