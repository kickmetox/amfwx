"""Database and HTTP client tests."""

from __future__ import annotations

import json
import os
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import Database, HttpClient


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        body = json.dumps({"ok": True, "path": self.path}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        payload = self.rfile.read(length).decode()
        body = json.dumps({"received": payload}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class DatabaseTests(unittest.TestCase):
    def test_crud(self):
        with Database() as db:
            db.execute("create table items (name text, value integer)")
            db.execute("insert into items values (?, ?)", ("a", 1))
            db.execute("insert into items values (?, ?)", ("b", 2))
            self.assertEqual(db.one("select value from items where name=?",
                                    ("b",))["value"], 2)
            self.assertEqual(len(db.query("select * from items")), 2)


class NetworkTests(unittest.TestCase):
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

    def test_get_post(self):
        client = HttpClient(self.base)
        self.assertTrue(client.json("/health")["ok"])
        result = client.json("/echo", method="POST", json_data={"a": 1})
        self.assertIn('"a": 1', result["received"])

    def test_rejects_file_url(self):
        with self.assertRaises(Exception):
            HttpClient("file:///C:/Windows").request("/x")


if __name__ == "__main__":
    unittest.main(verbosity=2)
