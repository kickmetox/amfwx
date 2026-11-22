"""Vision helper tests."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import image_base64, image_data_url, vision_message
from amfwx.ai import OpenAICompatibleProvider


class VisionTests(unittest.TestCase):
    def test_image_helpers(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "pixel.png")
            with open(path, "wb") as handle:
                handle.write(b"\x89PNG\r\n\x1a\n")
            self.assertTrue(image_base64(path))
            self.assertTrue(image_data_url(path).startswith("data:image/png;base64,"))
            message = vision_message("Was ist das?", path)
            self.assertEqual(message["role"], "user")
            self.assertEqual(len(message["images"]), 1)

    def test_openai_message_transform(self):
        provider = OpenAICompatibleProvider()
        messages = provider._vision_messages([
            {"role": "user", "content": "Bild", "images": ["abc"]}])
        self.assertEqual(messages[0]["content"][0]["type"], "text")
        self.assertEqual(messages[0]["content"][1]["type"], "image_url")
        self.assertTrue(messages[0]["content"][1]["image_url"]["url"].startswith(
            "data:image/png;base64,"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
