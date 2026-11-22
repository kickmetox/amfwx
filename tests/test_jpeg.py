"""Pure-Python baseline JPEG decoder."""

from __future__ import annotations

import base64
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import Canvas, Color, decode_webp, encode_webp, probe_webp
from amfwx.jpeg import decode_jpeg

JPEG = base64.b64decode(
    "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoH"
    "BwYIDAoMDAsKCwsNDhIQDQ4RDgsLEBYQERMUFRUVDA8XGBYUGBIUFRT/2wBDAQME"
    "BAUEBQkFBQkUDQsNFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQU"
    "FBQUFBQUFBQUFBQUFBT/wAARCAAQABADASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEA"
    "AAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIh"
    "MUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6"
    "Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZ"
    "mqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx"
    "8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREA"
    "AgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAV"
    "YnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hp"
    "anN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPE"
    "xcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD5"
    "0ooor8MP9Uz/2Q=="
)


class JPEGTests(unittest.TestCase):
    def test_decode_red(self):
        width, height, pixels = decode_jpeg(JPEG)
        self.assertEqual((width, height), (16, 16))
        canvas = Canvas(width, height)
        canvas.data[:] = pixels
        color = canvas.pixel(8, 8)
        self.assertGreater(color.r, 200)
        self.assertLess(color.g, 50)

    def test_webp_roundtrip(self):
        if not probe_webp():
            self.skipTest("libwebp nicht verfügbar")
        image = Canvas(8, 6, Color(200, 10, 20))
        data = encode_webp(image)
        self.assertGreater(len(data), 10)
        width, height, pixels = decode_webp(data)
        self.assertEqual((width, height), (8, 6))
        decoded = Canvas(width, height)
        decoded.data[:] = pixels
        color = decoded.pixel(4, 3)
        self.assertGreater(color.r, 150)


if __name__ == "__main__":
    unittest.main(verbosity=2)
