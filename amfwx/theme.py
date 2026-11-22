"""AMFWX themes and metrics."""

from __future__ import annotations

from dataclasses import dataclass

from .canvas import Color


@dataclass
class Theme:
    name: str = "dark"
    background: Color = Color(24, 26, 32)
    surface: Color = Color(34, 37, 44)
    surface_alt: Color = Color(42, 46, 54)
    text: Color = Color(232, 236, 244)
    muted: Color = Color(150, 158, 172)
    accent: Color = Color(59, 130, 246)
    accent_text: Color = Color(255, 255, 255)
    border: Color = Color(62, 68, 80)
    focus: Color = Color(96, 165, 250)
    danger: Color = Color(239, 91, 91)
    success: Color = Color(52, 199, 123)
    radius: int = 8
    padding: int = 8
    control_height: int = 32


DARK = Theme()
LIGHT = Theme(
    name="light", background=Color(245, 246, 248),
    surface=Color(255, 255, 255), surface_alt=Color(238, 241, 245),
    text=Color(28, 31, 36), muted=Color(100, 106, 116),
    accent=Color(37, 99, 235), accent_text=Color(255, 255, 255),
    border=Color(210, 215, 222), focus=Color(37, 99, 235),
)
HIGH_CONTRAST = Theme(
    name="high_contrast", background=Color(0, 0, 0),
    surface=Color(0, 0, 0), surface_alt=Color(20, 20, 20),
    text=Color(255, 255, 0), muted=Color(255, 255, 128),
    accent=Color(255, 255, 0), accent_text=Color(0, 0, 0),
    border=Color(255, 255, 255), focus=Color(0, 255, 255),
    radius=2, padding=12, control_height=40,
)

THEMES = {"dark": DARK, "light": LIGHT, "high_contrast": HIGH_CONTRAST}


def get_theme(name="dark"):
    return THEMES.get(str(name).lower(), DARK)
