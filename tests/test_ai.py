"""LLM provider tests with a local HTTP mock."""

from __future__ import annotations

import json
import os
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import OllamaProvider, OpenAICompatibleProvider


class Handler(BaseHTTPRequestHandler):
    payloads = []

    def log_message(self, *args):
        pass

    def _send(self, data):
        body = json.dumps(data).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/api/tags":
            self._send({"models": [{"name": "llama3.2"}]})
        elif self.path == "/v1/models":
            self._send({"data": [{"id": "local-model"}]})
        else:
            self.send_error(404)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(length) or b"{}")
        Handler.payloads.append((self.path, payload))
        if self.path == "/api/chat":
            self._send({"message": {
                "content": "ollama answer",
                "tool_calls": [{"function": {"name": "add_widget",
                                             "arguments": {"kind": "label"}}}]}})
        elif self.path == "/v1/chat/completions":
            self._send({"choices": [{"message": {
                "content": "openai answer",
                "tool_calls": [{"id": "c1", "function": {
                    "name": "add_widget",
                    "arguments": json.dumps({"kind": "button"})}}]}}]})
        else:
            self.send_error(404)


class AITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever,
                                      daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def test_ollama(self):
        provider = OllamaProvider(model="llama3.2", base_url=self.base)
        self.assertEqual(provider.list_models(), ["llama3.2"])
        result = provider.chat([{"role": "user", "content": "hi"}],
                               tools=[{"type": "function"}])
        self.assertEqual(result["content"], "ollama answer")
        self.assertEqual(result["tool_calls"][0]["name"], "add_widget")
        self.assertEqual(result["tool_calls"][0]["arguments"],
                         {"kind": "label"})

    def test_openai_compatible(self):
        provider = OpenAICompatibleProvider(model="local-model",
                                            base_url=self.base + "/v1")
        self.assertEqual(provider.list_models(), ["local-model"])
        result = provider.chat([{"role": "user", "content": "hi"}])
        self.assertEqual(result["content"], "openai answer")
        self.assertEqual(result["tool_calls"][0]["arguments"],
                         {"kind": "button"})


if __name__ == "__main__":
    unittest.main(verbosity=2)
