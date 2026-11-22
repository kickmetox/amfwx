"""Minimal mixer UI built on the DSP layer."""

from __future__ import annotations

from .canvas import Rect
from .widgets import Label, Slider, Widget


class MixerStrip(Widget):
    def __init__(self, name, gain=1.0, on_change=None):
        super().__init__()
        self.name = str(name)
        self.gain = float(gain)
        self.on_change = on_change
        self.title = Label(self.name)
        self.slider = Slider(0, 200, int(self.gain * 100))
        self.slider.on_change = self._changed
        self.title.parent = self
        self.slider.parent = self

    def _changed(self, value):
        self.gain = value / 100.0
        if self.on_change is not None:
            self.on_change(self.name, self.gain)

    def arrange(self, rect):
        self.rect = rect
        self.title.arrange(Rect(rect.x, rect.y, rect.w, 20))
        self.slider.arrange(Rect(rect.x + 4, rect.y + 24,
                                 max(8, rect.w - 8),
                                 max(8, rect.h - 28)))

    def state(self):
        return {"name": self.name, "gain": self.gain}

    def apply_state(self, state):
        self.gain = max(0.0, min(2.0, float(state.get("gain", 1.0))))
        self.slider._value = int(self.gain * 100)
        return self

    def paint(self, canvas):
        self.title.paint(canvas)
        self.slider.paint(canvas)


class MixerPanel(Widget):
    def __init__(self, strips=None):
        super().__init__()
        self.strips = list(strips or [])
        for strip in self.strips:
            strip.parent = self

    def add(self, strip):
        strip.parent = self
        self.strips.append(strip)
        return strip

    def arrange(self, rect):
        self.rect = rect
        if not self.strips:
            return
        width = rect.w / len(self.strips)
        for index, strip in enumerate(self.strips):
            strip.arrange(Rect(rect.x + index * width, rect.y,
                               max(1, width - 4), rect.h))

    def state(self):
        return {strip.name: strip.gain for strip in self.strips}

    def save_file(self, path):
        import json
        from pathlib import Path as _Path
        _Path(path).write_text(json.dumps(self.state(), indent=2),
                               encoding="utf-8")
        return self

    def load_file(self, path):
        import json
        from pathlib import Path as _Path
        self.apply_state(json.loads(_Path(path).read_text(encoding="utf-8")))
        return self

    def save_presets(self, settings, key="mixer"):
        settings.set(key, self.state())
        return self

    def load_presets(self, settings, key="mixer"):
        self.apply_state(dict(settings.get(key, {})))
        return self

    def apply_state(self, state):
        for strip in self.strips:
            if strip.name in state:
                strip.apply_state({"gain": state[strip.name]})
        return self

    def paint(self, canvas):
        for strip in self.strips:
            strip.paint(canvas)
