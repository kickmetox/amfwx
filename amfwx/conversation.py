"""Conversation persistence for AI sessions."""

from __future__ import annotations

import json
from pathlib import Path


class Conversation:
    def __init__(self, messages=None):
        self.messages = list(messages or [])

    def add(self, role, content):
        self.messages.append({"role": str(role), "content": str(content)})
        return self

    def clear(self):
        self.messages.clear()
        return self

    def to_messages(self):
        return list(self.messages)

    def save(self, path):
        Path(path).write_text(json.dumps(self.messages, indent=2,
                                         ensure_ascii=False),
                              encoding="utf-8")
        return self

    @classmethod
    def load(cls, path):
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise ValueError("conversation must be a list")
        return cls(data)

    def __len__(self):
        return len(self.messages)
