"""MCP client/server tests."""

from __future__ import annotations

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from amfwx.mcp import MCPClient, MCPServer


class MCPTests(unittest.TestCase):
    def test_server_handle(self):
        server = MCPServer()
        init = server.handle({"jsonrpc": "2.0", "id": 1,
                              "method": "initialize",
                              "params": {}})
        self.assertEqual(init["result"]["serverInfo"]["name"], "amfwx")
        tools = server.handle({"jsonrpc": "2.0", "id": 2,
                               "method": "tools/list"})
        names = {tool["function"]["name"]
                 for tool in tools["result"]["tools"]}
        self.assertIn("create_window", names)
        result = server.handle({
            "jsonrpc": "2.0", "id": 3, "method": "tools/call",
            "params": {"name": "create_window",
                       "arguments": {"title": "MCP"}}})
        self.assertTrue(result["result"]["content"])
        server.session.close()

    def test_client_stdio(self):
        client = MCPClient([sys.executable, "-m", "amfwx.mcp"], cwd=ROOT)
        try:
            info = client.initialize()
            self.assertEqual(info["serverInfo"]["name"], "amfwx")
            tools = client.list_tools()
            self.assertTrue(any(tool["function"]["name"] == "create_window"
                                for tool in tools))
            result = client.call_tool("add_widget",
                                      {"kind": "label", "text": "MCP"})
            self.assertIn("content", result)
        finally:
            client.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
