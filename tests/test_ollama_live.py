"""Optional live Ollama test.

Run only when a real Ollama server and model are available:

    $env:AMFWX_OLLAMA_TEST="1"
    python -m unittest tests.test_ollama_live -v
"""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import OllamaProvider


@unittest.skipUnless(os.environ.get("AMFWX_OLLAMA_TEST") == "1",
                     "AMFWX_OLLAMA_TEST nicht gesetzt")
class OllamaLiveTests(unittest.TestCase):
    def test_chat(self):
        model = os.environ.get("AMFWX_OLLAMA_MODEL", "llama3.2")
        provider = OllamaProvider(model=model, retries=1, backoff=0.2)
        models = provider.list_models()
        self.assertTrue(models)
        result = provider.chat([{"role": "user", "content": "Say OK"}])
        self.assertIsInstance(result["content"], str)


if __name__ == "__main__":
    unittest.main(verbosity=2)
