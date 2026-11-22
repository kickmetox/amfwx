"""AI extras: streaming, conversation, key store, progress widget."""

from __future__ import annotations

import json
import os
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import (Conversation, KeyStore, OllamaProvider,
                   OpenAICompatibleProvider, UiSession)


class StreamHandler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_POST(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.end_headers()
        if self.path == "/api/chat":
            self.wfile.write(b'{"message":{"content":"a"},"done":false}\n')
            self.wfile.write(b'{"message":{"content":"b"},"done":true}\n')
        else:
            self.wfile.write(b'data: {"choices":[{"delta":{"content":"x"}}]}\n\n')
            self.wfile.write(b'data: [DONE]\n\n')


class AIExtrasTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), StreamHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever,
                                      daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def test_streaming(self):
        ollama = OllamaProvider(base_url=self.base)
        parts = [item["content"] for item in ollama.stream_chat(
            [{"role": "user", "content": "hi"}])]
        self.assertEqual(parts, ["a", "b"])
        openai = OpenAICompatibleProvider(base_url=self.base + "/v1")
        parts = [item["content"] for item in openai.stream_chat(
            [{"role": "user", "content": "hi"}])]
        self.assertEqual(parts, ["x"])

    def test_conversation(self):
        conversation = Conversation()
        conversation.add("user", "Hallo").add("assistant", "Hi")
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "chat.json")
            conversation.save(path)
            loaded = Conversation.load(path)
            self.assertEqual(loaded.to_messages(), conversation.to_messages())
            self.assertEqual(len(loaded), 2)

    def test_keystore(self):
        with tempfile.TemporaryDirectory() as folder:
            store = KeyStore(folder)
            store.save("token", "secret-value")
            self.assertEqual(store.load("token"), "secret-value")
            self.assertTrue(store.delete("token"))
            self.assertIsNone(store.load("token"))

    def test_progress_tool(self):
        session = UiSession()
        try:
            session.create_window("Progress", 300, 200)
            result = session.add_widget("progress", "40", 20, 20, 200, 10)
            self.assertTrue(result["ok"])
            self.assertEqual(session.widgets[result["id"]].value(), 40)
        finally:
            session.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
