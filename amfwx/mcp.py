"""Minimal Model Context Protocol (MCP) stdio client/server."""

from __future__ import annotations

import json
import subprocess
import sys

from .llm_tools import TOOL_SPECS, UiSession, call_tool


class MCPError(RuntimeError):
    pass


class MCPClient:
    def __init__(self, command, cwd=None):
        self.command = list(command)
        self.process = subprocess.Popen(
            self.command, cwd=cwd, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            bufsize=1)
        self._id = 0

    def _send(self, payload):
        self.process.stdin.write(json.dumps(payload) + "\n")
        self.process.stdin.flush()

    def _read(self):
        line = self.process.stdout.readline()
        if not line:
            error = self.process.stderr.read() if self.process.stderr else ""
            raise MCPError(f"MCP-Server beendet: {error.strip()}")
        return json.loads(line)

    def request(self, method, params=None):
        self._id += 1
        request_id = self._id
        self._send({"jsonrpc": "2.0", "id": request_id, "method": method,
                    "params": params or {}})
        while True:
            response = self._read()
            if response.get("id") == request_id:
                if "error" in response:
                    raise MCPError(str(response["error"]))
                return response.get("result", {})

    def initialize(self):
        result = self.request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "amfwx", "version": "3.15.0"},
        })
        self._send({"jsonrpc": "2.0", "method": "notifications/initialized",
                    "params": {}})
        return result

    def list_tools(self):
        return self.request("tools/list").get("tools", [])

    def call_tool(self, name, arguments=None):
        return self.request("tools/call", {"name": name,
                                           "arguments": arguments or {}})

    def close(self):
        if self.process.poll() is None:
            try:
                self.process.stdin.close()
            except Exception:
                pass
            self.process.terminate()
            try:
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.process.kill()
        for stream in (self.process.stdin, self.process.stdout,
                       self.process.stderr):
            try:
                stream.close()
            except Exception:
                pass
        return self


class MCPServer:
    def __init__(self, session=None):
        self.session = session or UiSession()
        self.initialized = False

    def handle(self, request):
        method = request.get("method", "")
        request_id = request.get("id")
        if method == "initialize":
            self.initialized = True
            return {"jsonrpc": "2.0", "id": request_id, "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "amfwx",
                               "version": __import__("amfwx").__version__},
            }}
        if method == "notifications/initialized":
            return None
        if method == "tools/list":
            return {"jsonrpc": "2.0", "id": request_id,
                    "result": {"tools": list(TOOL_SPECS)}}
        if method == "tools/call":
            params = request.get("params") or {}
            result = call_tool(self.session, params.get("name", ""),
                               params.get("arguments") or {})
            return {"jsonrpc": "2.0", "id": request_id, "result": {
                "content": [{"type": "text", "text": json.dumps(result,
                                                               ensure_ascii=False)}],
                "isError": not result.get("ok", False),
            }}
        return {"jsonrpc": "2.0", "id": request_id, "error": {
            "code": -32601, "message": f"unknown method: {method}"}}

    def serve(self, instream=None, outstream=None):
        instream = instream or sys.stdin
        outstream = outstream or sys.stdout
        for line in instream:
            line = line.strip()
            if not line:
                continue
            try:
                request = json.loads(line)
            except ValueError:
                continue
            response = self.handle(request)
            if response is not None:
                outstream.write(json.dumps(response) + "\n")
                outstream.flush()
        self.session.close()


def main():
    MCPServer().serve()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
