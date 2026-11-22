"""Shared theme/event contracts between AMFW and AMFWX."""

from __future__ import annotations

from dataclasses import dataclass

from .theme import DARK, Theme


@dataclass
class ThemeTokens:
    background: str = "#181a20"
    surface: str = "#22252c"
    text: str = "#e8ecf4"
    accent: str = "#3b82f6"
    border: str = "#3e4450"
    focus: str = "#60a5fa"
    radius: int = 8
    control_height: int = 32


def _hex(color):
    if hasattr(color, "r"):
        return f"#{color.r:02x}{color.g:02x}{color.b:02x}"
    return str(color)


def from_amfw(theme):
    return ThemeTokens(
        background=_hex(theme.window), surface=_hex(theme.surface),
        text=_hex(theme.text), accent=_hex(theme.accent),
        border=_hex(theme.border), focus=_hex(theme.focus),
        radius=int(getattr(theme, "radius", 8)),
        control_height=int(getattr(theme, "control_height", 32)),
    )


def to_amfwx(tokens):
    from .canvas import Color

    return Theme(
        background=Color.from_hex(tokens.background),
        surface=Color.from_hex(tokens.surface),
        text=Color.from_hex(tokens.text),
        accent=Color.from_hex(tokens.accent),
        border=Color.from_hex(tokens.border),
        focus=Color.from_hex(tokens.focus),
        radius=tokens.radius,
        control_height=tokens.control_height,
    )


@dataclass
class PointerEvent:
    x: int = 0
    y: int = 0
    button: str = "left"
    kind: str = "down"


def from_amfw_event(event):
    kind = getattr(event, "type", "mouse")
    return PointerEvent(int(getattr(event, "x", 0)),
                        int(getattr(event, "y", 0)),
                        getattr(event, "button", "left"), kind)
