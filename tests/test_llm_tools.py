"""UI tool and agent tests."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import EchoProvider, LLMAgent, TOOL_SPECS, UiSession, call_tool


class ToolTests(unittest.TestCase):
    def test_ui_tools(self):
        session = UiSession()
        try:
            self.assertTrue(session.create_window("SDK", 320, 200)["ok"])
            clicked = []
            result = session.add_widget("button", "OK", 20, 20, 100, 32)
            button_id = result["id"]
            session.widgets[button_id].on_click = lambda: clicked.append(1)
            self.assertTrue(session.set_widget_text(button_id, "Start")["ok"])
            self.assertTrue(session.click(button_id)["ok"])
            self.assertEqual(clicked, [1])
            self.assertEqual(session.list_widgets()[0]["text"], "Start")
            with tempfile.TemporaryDirectory() as folder:
                path = os.path.join(folder, "ui.png")
                self.assertTrue(session.snapshot(path)["ok"])
                self.assertGreater(os.path.getsize(path), 0)
        finally:
            session.close()

    def test_tool_specs_and_call(self):
        names = {tool["function"]["name"] for tool in TOOL_SPECS}
        self.assertIn("create_window", names)
        self.assertIn("add_widget", names)
        session = UiSession()
        try:
            result = call_tool(session, "create_window",
                               {"title": "Tools"})
            self.assertTrue(result["ok"])
            result = call_tool(session, "add_widget",
                               {"kind": "label", "text": "Hallo"})
            self.assertTrue(result["ok"])
            result = call_tool(session, "unknown", {})
            self.assertFalse(result["ok"])
        finally:
            session.close()


class ScriptProvider:
    def __init__(self, responses):
        self.responses = list(responses)
        self.last_tools = None

    def chat(self, messages, tools=None):
        self.last_tools = tools
        return self.responses.pop(0)


class AgentTests(unittest.TestCase):
    def test_agent_executes_tools(self):
        provider = ScriptProvider([
            {"content": "", "tool_calls": [
                {"name": "create_window",
                 "arguments": {"title": "Agent", "width": 320, "height": 200}},
                {"name": "add_widget",
                 "arguments": {"kind": "label", "text": "Hallo"}},
            ]},
            {"content": "Fertig", "tool_calls": []},
        ])
        session = UiSession()
        agent = LLMAgent(provider, session=session)
        try:
            self.assertEqual(agent.run("Baue ein Fenster"), "Fertig")
            self.assertEqual(session.list_widgets()[0]["text"], "Hallo")
            self.assertTrue(provider.last_tools)
        finally:
            agent.close()

    def test_echo_agent(self):
        session = UiSession()
        agent = LLMAgent(EchoProvider(), session=session)
        try:
            self.assertIn("echo:", agent.run("Hallo"))
        finally:
            agent.close()

    def test_app_tools_disabled(self):
        session = UiSession()
        result = call_tool(session, "list_devices", {})
        self.assertFalse(result["ok"])
        self.assertIn("deaktiviert", result["error"])

    def test_streaming(self):
        class Provider:
            def chat(self, messages, tools=None):
                return {"content": "done", "tool_calls": []}
            def stream_chat(self, messages, tools=None):
                yield {"content": "Hal"}
                yield {"content": "lo"}
        agent = LLMAgent(Provider(), session=UiSession())
        self.assertEqual("".join(agent.run_stream("hi")), "Hallo")
        agent.close()

    def test_async_run(self):
        import asyncio
        agent = LLMAgent(EchoProvider(), session=UiSession())
        result = asyncio.run(agent.async_run("hallo"))
        self.assertIn("hallo", result)
        agent.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
