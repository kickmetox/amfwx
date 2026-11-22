"""Image helpers for vision-capable LLM providers."""

from __future__ import annotations

import base64
import mimetypes
from pathlib import Path


def image_base64(path):
    data = Path(path).read_bytes()
    return base64.b64encode(data).decode("ascii")


def image_data_url(path):
    path = Path(path)
    mime = mimetypes.guess_type(path.name)[0] or "image/png"
    return f"data:{mime};base64,{image_base64(path)}"


def vision_message(text, path):
    return {"role": "user", "content": str(text),
            "images": [image_base64(path)]}


def openai_vision_content(text, path):
    return [
        {"type": "text", "text": str(text)},
        {"type": "image_url", "image_url": {"url": image_data_url(path)}},
    ]
