"""Agent loop connecting an LLM provider to AMFWX UI tools."""

from __future__ import annotations

import json

from .llm_tools import TOOL_SPECS, UiSession, call_tool, tool_result_text


SYSTEM_PROMPT = """You are an AMFWX UI assistant. Use the provided tools to
create a window and widgets. Prefer clear layouts, readable labels and
accessible text. Do not invent tool names. After the UI is built, summarize
what you created. Available widget kinds: label, button, line_edit,
text_edit, checkbox, slider, combo."""


class LLMAgent:
    def __init__(self, provider, session=None, system_prompt=None,
                 max_steps=8):
        self.provider = provider
        self.session = session or UiSession()
        self.system_prompt = system_prompt or SYSTEM_PROMPT
        self.max_steps = max(1, int(max_steps))
        self.messages = [{"role": "system", "content": self.system_prompt}]
        self.last_tool_results = []
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run(self, text, image=None):
        self._cancelled = False
        message = {"role": "user", "content": str(text)}
        if image is not None:
            from .vision import image_base64
            message["images"] = [image_base64(image)]
        self.messages.append(message)
        for _ in range(self.max_steps):
            if self._cancelled:
                return "abgebrochen"
            response = self.provider.chat(self.messages, tools=TOOL_SPECS)
            calls = response.get("tool_calls") or []
            content = response.get("content") or ""
            if not calls:
                self.messages.append({"role": "assistant",
                                      "content": content})
                return content
            assistant = {"role": "assistant", "content": content}
            openai_calls = []
            for call in calls:
                openai_calls.append({
                    "id": call.get("id", ""),
                    "type": "function",
                    "function": {
                        "name": call.get("name", ""),
                        "arguments": json.dumps(call.get("arguments", {})),
                    },
                })
            if openai_calls:
                assistant["tool_calls"] = openai_calls
            self.messages.append(assistant)
            for call in calls:
                if self._cancelled:
                    return "abgebrochen"
                result = call_tool(self.session, call.get("name", ""),
                                   call.get("arguments", {}))
                self.last_tool_results.append(result)
                self.messages.append({
                    "role": "tool",
                    "name": call.get("name", ""),
                    "content": tool_result_text(result),
                })
        return "max_steps erreicht"

    def run_stream(self, text, image=None):
        """Yield content chunks; tool calls are not executed in this mode."""
        self._cancelled = False
        message = {"role": "user", "content": str(text)}
        if image is not None:
            from .vision import image_base64
            message["images"] = [image_base64(image)]
        self.messages.append(message)
        if not hasattr(self.provider, "stream_chat"):
            response = self.provider.chat(self.messages)
            content = response.get("content") or ""
            if content:
                yield content
            self.messages.append({"role": "assistant", "content": content})
            return
        chunks = []
        for chunk in self.provider.stream_chat(self.messages):
            if self._cancelled:
                break
            content = chunk.get("content") or ""
            if content:
                chunks.append(content)
                yield content
        self.messages.append({"role": "assistant",
                              "content": "".join(chunks)})

    def close(self):
        self.session.close()
