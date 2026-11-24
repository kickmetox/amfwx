"""Unified SDK facade for AMFWX, bridges and LLM tools."""

from __future__ import annotations

from .agent import LLMAgent
from .ai import (AIError, EchoProvider, OllamaProvider,
                 OpenAICompatibleProvider, provider_from_name)
from .llm_tools import TOOL_SPECS, UiSession, call_tool


class SDK:
    def __init__(self, theme="dark"):
        self.ui = UiSession(theme=theme)
        self.providers = {
            "ollama": OllamaProvider,
            "openai": OpenAICompatibleProvider,
            "echo": EchoProvider,
        }

    def provider(self, name="ollama", **kwargs):
        return provider_from_name(name, **kwargs)

    def agent(self, provider=None, **kwargs):
        if provider is None:
            provider = EchoProvider()
        return LLMAgent(provider, session=self.ui, **kwargs)

    def create_window(self, *args, **kwargs):
        return self.ui.create_window(*args, **kwargs)

    def add_widget(self, *args, **kwargs):
        return self.ui.add_widget(*args, **kwargs)

    def tools(self):
        return list(TOOL_SPECS)

    def call_tool(self, name, arguments):
        return call_tool(self.ui, name, arguments)

    def snapshot(self, path=None):
        return self.ui.snapshot(path)

    def run(self):
        return self.ui.run()

    def close(self):
        self.ui.close()

    # Optional AMFW bridges are imported lazily so AMFW is not a hard
    # dependency of the SDK.
    def amfwx_view(self, root, width=420, height=260, theme=None):
        from .amfw_bridge import AmfwxView
        return AmfwxView(root, width, height, theme)

    def amfw_host(self, amfw_window):
        from .amfw_bridge import AmfwxWindowHost
        return AmfwxWindowHost(amfw_window)


def create_sdk(theme="dark"):
    return SDK(theme=theme)


def main(argv=None):
    import argparse
    import json
    parser = argparse.ArgumentParser(prog="amfwx-sdk")
    parser.add_argument("--tools", action="store_true",
                        help="print the LLM tool schemas")
    parser.add_argument("--snapshot", metavar="PNG",
                        help="render a small demo window")
    parser.add_argument("--version", action="store_true")
    args = parser.parse_args(argv)
    if args.version:
        from . import __version__
        print(__version__)
        return 0
    if args.tools:
        print(json.dumps(TOOL_SPECS, indent=2, ensure_ascii=False))
        return 0
    if args.snapshot:
        sdk = create_sdk()
        try:
            sdk.call_tool("create_window", {"title": "AMFWX SDK",
                                            "width": 420, "height": 240})
            sdk.call_tool("add_widget", {"kind": "label", "text": "AMFWX SDK",
                                         "x": 24, "y": 24})
            sdk.call_tool("add_widget", {"kind": "button", "text": "OK",
                                         "x": 24, "y": 72})
            print(sdk.snapshot(args.snapshot)["path"])
        finally:
            sdk.close()
        return 0
    parser.print_help()
    return 0
