"""AMFWX advanced widgets: tabs, tooltips, charts and property grid."""

from __future__ import annotations

from dataclasses import dataclass, field

from .canvas import Canvas, Color, Rect
from .text import draw_text, measure_text
from .widgets import LineEdit, Panel, Widget


class TabView(Widget):
    def __init__(self, on_change=None):
        super().__init__()
        self.tabs = []
        self.active = 0
        self.on_change = on_change

    def add_tab(self, title, widget):
        widget.parent = self
        widget.visible = False
        self.tabs.append((str(title), widget))
        if len(self.tabs) == 1:
            widget.visible = True
        return widget

    def size_hint(self):
        return (420, 280)

    def _tab_rects(self):
        rects = []
        x = self.rect.x + 4
        for title, _widget in self.tabs:
            width = measure_text(title, 2) + 20
            rects.append(Rect(x, self.rect.y, width, 30))
            x += width
        return rects

    def paint(self, canvas):
        theme = self.theme()
        canvas.fill_rect(Rect(self.rect.x, self.rect.y, self.rect.w, 30),
                         theme.surface_alt)
        for index, ((title, _widget), rect) in enumerate(
                zip(self.tabs, self._tab_rects())):
            if index == self.active:
                canvas.fill_rect(rect, theme.surface)
                canvas.fill_rect(Rect(rect.x, rect.bottom - 2, rect.w, 2),
                                 theme.accent)
            draw_text(canvas, title, rect.x + 10, rect.y + 8,
                      theme.text, 2)
        if self.tabs and 0 <= self.active < len(self.tabs):
            page = self.tabs[self.active][1]
            page.visible = True
            page.paint(canvas)

    def arrange(self, rect):
        self.rect = rect
        for index, (_title, page) in enumerate(self.tabs):
            page.visible = index == self.active
            page.arrange(Rect(rect.x, rect.y + 30, rect.w,
                              max(1, rect.h - 30)))

    def mouse_up(self, x, y, button="left"):
        for index, rect in enumerate(self._tab_rects()):
            if rect.contains(x, y):
                self.active = index
                for page_index, (_title, page) in enumerate(self.tabs):
                    page.visible = page_index == index
                if self.on_change:
                    self.on_change(index)
                self.arrange(self.rect)
                return


class Tooltip(Widget):
    def __init__(self, text="", parent=None):
        super().__init__()
        self.text = text
        if parent is not None:
            self.parent = parent

    def size_hint(self):
        return (measure_text(self.text, 2) + 16, 28)

    def paint(self, canvas):
        theme = self.theme()
        canvas.rounded_rect(self.rect, 4, theme.surface_alt)
        canvas.draw_rect(self.rect, theme.border, 1)
        draw_text(canvas, self.text, self.rect.x + 8, self.rect.y + 7,
                  theme.text, 2)


@dataclass
class Series:
    name: str
    points: list = field(default_factory=list)
    color: Color = Color(80, 150, 240)


class Chart(Widget):
    def __init__(self, title=""):
        super().__init__()
        self.title = title
        self.series = []
        self.kind = "line"

    def add_series(self, name, points, color=None):
        self.series.append(Series(str(name), list(points),
                                  color or Color(80, 150, 240)))
        return self

    def size_hint(self):
        return (420, 260)

    def paint(self, canvas):
        theme = self.theme()
        canvas.rounded_rect(self.rect, theme.radius, theme.surface)
        plot = Rect(self.rect.x + 42, self.rect.y + 30,
                    max(10, self.rect.w - 58), max(10, self.rect.h - 54))
        if self.title:
            draw_text(canvas, self.title, self.rect.x + 10, self.rect.y + 7,
                      theme.text, 2)
        points = [point for series in self.series for point in series.points]
        if not points:
            return
        xs = [point[0] for point in points]
        ys = [point[1] for point in points]
        x0, x1 = min(xs), max(xs)
        y0, y1 = min(ys), max(ys)
        if x0 == x1:
            x1 = x0 + 1
        if y0 == y1:
            y1 = y0 + 1
        for index in range(5):
            x = plot.x + plot.w * index / 4
            y = plot.y + plot.h * index / 4
            canvas.line(x, plot.y, x, plot.bottom,
                        theme.border.with_alpha(80), 1)
            canvas.line(plot.x, y, plot.right, y,
                        theme.border.with_alpha(80), 1)
        for series in self.series:
            mapped = [(plot.x + (px - x0) / (x1 - x0) * plot.w,
                       plot.bottom - (py - y0) / (y1 - y0) * plot.h)
                      for px, py in series.points]
            if self.kind == "bar":
                width = max(2, plot.w / max(1, len(mapped)) * 0.6)
                for px, py in mapped:
                    canvas.fill_rect(Rect(px - width / 2, py, width,
                                          plot.bottom - py), series.color)
            else:
                canvas.polyline(mapped, series.color, 2)
                for px, py in mapped:
                    canvas.fill_circle(px, py, 3, series.color)


@dataclass
class Property:
    name: str
    label: str = ""
    kind: str = "str"
    value: object = ""


class PropertyGrid(Widget):
    def __init__(self, properties=None, on_change=None):
        super().__init__()
        self.properties = list(properties or [])
        self.on_change = on_change
        self.editors = {}

    def add(self, prop):
        self.properties.append(prop)
        return prop

    def size_hint(self):
        return (360, 30 * max(1, len(self.properties)) + 16)

    def arrange(self, rect):
        self.rect = rect
        self.editors.clear()
        y = rect.y + 8
        for prop in self.properties:
            editor = LineEdit(str(prop.value))
            editor.on_change = lambda value, item=prop: self._changed(item, value)
            editor.arrange(Rect(rect.x + 140, y, max(80, rect.w - 148), 30))
            editor.parent = self
            self.editors[prop.name] = editor
            y += 34

    def _changed(self, prop, value):
        if prop.kind == "int":
            try:
                value = int(value)
            except ValueError:
                return
        prop.value = value
        if self.on_change:
            self.on_change(prop.name, value)

    def paint(self, canvas):
        theme = self.theme()
        canvas.fill_rect(self.rect, theme.surface)
        y = self.rect.y + 8
        for prop in self.properties:
            draw_text(canvas, prop.label or prop.name, self.rect.x + 8,
                      y + 7, theme.text, 2)
            editor = self.editors.get(prop.name)
            if editor is not None:
                editor.paint(canvas)
            y += 34

    def value(self, name):
        for prop in self.properties:
            if prop.name == name:
                return prop.value
        return None


class ImageView(Widget):
    def __init__(self, image=None, fit=True):
        super().__init__()
        self.image = image
        self.fit = fit
        self.zoom = 1.0
        self.pan = [0, 0]
        self._cache_key = None
        self._cache = None
        self._dragging = False
        self._drag = (0, 0)

    def size_hint(self):
        return (320, 240)

    def _render(self):
        if self.image is None:
            return None
        key = (self.rect.w, self.rect.h, self.zoom, self.pan[0],
               self.pan[1], self.fit)
        if key == self._cache_key:
            return self._cache
        image = self.image
        if self.fit:
            scale = min((self.rect.w - 8) / image.width,
                        (self.rect.h - 8) / image.height)
        else:
            scale = self.zoom
        width = max(1, int(image.width * scale))
        height = max(1, int(image.height * scale))
        scaled = image.scaled(width, height)
        self._cache = scaled
        self._cache_key = key
        return scaled

    def paint(self, canvas):
        canvas.fill_rect(self.rect, self.theme().surface)
        image = self._render()
        if image is None:
            return
        x = self.rect.x + (self.rect.w - image.width) / 2 + self.pan[0]
        y = self.rect.y + (self.rect.h - image.height) / 2 + self.pan[1]
        canvas.blit(image, int(x), int(y))

    def wheel(self, delta):
        self.zoom = max(0.1, min(8.0, self.zoom * (1.1 if delta > 0 else 0.9)))
        self.fit = False
        self._cache_key = None
        return self.zoom

    def mouse_down(self, x, y, button="left"):
        self._dragging = True
        self._drag = (x, y)

    def mouse_move(self, x, y):
        if self._dragging:
            self.pan[0] += x - self._drag[0]
            self.pan[1] += y - self._drag[1]
            self._drag = (x, y)
            self._cache_key = None

    def mouse_up(self, x, y, button="left"):
        self._dragging = False


class StatusBar(Widget):
    def __init__(self, fields=None):
        super().__init__()
        self.fields = list(fields or [""])

    def size_hint(self):
        return (400, 24)

    def set_field(self, index, text):
        while len(self.fields) <= index:
            self.fields.append("")
        self.fields[index] = str(text)

    def paint(self, canvas):
        theme = self.theme()
        canvas.fill_rect(self.rect, theme.surface_alt)
        canvas.line(self.rect.x, self.rect.y, self.rect.right, self.rect.y,
                    theme.border, 1)
        width = max(1, self.rect.w // max(1, len(self.fields)))
        for index, text in enumerate(self.fields):
            draw_text(canvas, str(text), self.rect.x + index * width + 8,
                      self.rect.y + 5, theme.muted, 1)
            if index:
                canvas.line(self.rect.x + index * width, self.rect.y + 4,
                            self.rect.x + index * width, self.rect.bottom - 4,
                            theme.border, 1)


class ToolBar(Widget):
    def __init__(self, actions=None):
        super().__init__()
        self.actions = list(actions or [])
        self.hover = -1
        self.pressed = -1

    def add(self, label, callback=None):
        self.actions.append((label, callback))
        return self

    def size_hint(self):
        return (400, 34)

    def _rects(self):
        x = self.rect.x + 4
        rects = []
        for label, _callback in self.actions:
            width = measure_text(label, 2) + 18
            rects.append(Rect(x, self.rect.y + 3, width, 28))
            x += width + 4
        return rects

    def paint(self, canvas):
        theme = self.theme()
        canvas.fill_rect(self.rect, theme.surface_alt)
        for index, ((label, _callback), rect) in enumerate(
                zip(self.actions, self._rects())):
            if index == self.hover:
                canvas.rounded_rect(rect, 4, theme.accent.with_alpha(60))
            draw_text(canvas, label, rect.x + 9, rect.y + 6, theme.text, 2)

    def mouse_move(self, x, y):
        self.hover = -1
        for index, rect in enumerate(self._rects()):
            if rect.contains(x, y):
                self.hover = index

    def mouse_down(self, x, y, button="left"):
        self.pressed = self.hover

    def mouse_up(self, x, y, button="left"):
        index = self.pressed
        self.pressed = -1
        if 0 <= index < len(self.actions) and self._rects()[index].contains(x, y):
            callback = self.actions[index][1]
            if callback:
                callback()


class Splitter(Widget):
    def __init__(self, first=None, second=None, orientation="horizontal",
                 ratio=0.5, on_change=None):
        super().__init__()
        self.first = first or Panel()
        self.second = second or Panel()
        self.orientation = orientation
        self.ratio = float(ratio)
        self.on_change = on_change
        self._dragging = False
        self.first.parent = self
        self.second.parent = self

    def size_hint(self):
        return (400, 240)

    def _divider(self):
        if self.orientation == "horizontal":
            x = self.rect.x + int(self.rect.w * self.ratio)
            return Rect(x - 3, self.rect.y, 6, self.rect.h)
        y = self.rect.y + int(self.rect.h * self.ratio)
        return Rect(self.rect.x, y - 3, self.rect.w, 6)

    def arrange(self, rect):
        self.rect = rect
        if self.orientation == "horizontal":
            split = int(rect.w * self.ratio)
            self.first.arrange(Rect(rect.x, rect.y, max(1, split - 3), rect.h))
            self.second.arrange(Rect(rect.x + split + 3, rect.y,
                                     max(1, rect.w - split - 3), rect.h))
        else:
            split = int(rect.h * self.ratio)
            self.first.arrange(Rect(rect.x, rect.y, rect.w, max(1, split - 3)))
            self.second.arrange(Rect(rect.x, rect.y + split + 3, rect.w,
                                     max(1, rect.h - split - 3)))

    def paint(self, canvas):
        theme = self.theme()
        self.first.paint(canvas)
        self.second.paint(canvas)
        canvas.fill_rect(self._divider(), theme.border)

    def mouse_down(self, x, y, button="left"):
        if self._divider().contains(x, y):
            self._dragging = True

    def mouse_move(self, x, y):
        if not self._dragging:
            return
        if self.orientation == "horizontal":
            self.ratio = max(0.05, min(0.95, (x - self.rect.x) / max(1, self.rect.w)))
        else:
            self.ratio = max(0.05, min(0.95, (y - self.rect.y) / max(1, self.rect.h)))
        self.arrange(self.rect)
        if self.on_change:
            self.on_change(self.ratio)

    def mouse_up(self, x, y, button="left"):
        self._dragging = False


class VideoView(Widget):
    def __init__(self, video, fit=True):
        super().__init__()
        from .video import VideoPlayer
        self.video = video
        self.player = VideoPlayer(video)
        self.stream = video.stream() if hasattr(video, "stream") else None
        self.current = None
        self.fit = fit
        self.playing = True
        self._cache = None
        self._cache_index = -1

    def size_hint(self):
        if self.video and self.video.width:
            return (self.video.width, self.video.height)
        return (320, 240)

    def play(self):
        self.playing = True

    def pause(self):
        self.playing = False

    def advance(self, seconds):
        if self.stream is not None:
            if self.playing:
                frame = self.stream.next_frame()
                if frame is not None:
                    self.current = frame
                    self._cache = None
            return self.current
        if self.playing:
            self.player.advance(seconds)
            self._cache = None
        return self.player.frame()

    def paint(self, canvas):
        theme = self.theme()
        canvas.fill_rect(self.rect, theme.surface)
        frame = self.current if self.stream is not None else self.player.frame()
        if frame is None:
            return
        scale = min(self.rect.w / frame.width, self.rect.h / frame.height)
        width = max(1, int(frame.width * scale))
        height = max(1, int(frame.height * scale))
        if self._cache is None or self._cache_index != self.player.frame_index():
            self._cache = frame.scaled(width, height)
            self._cache_index = self.player.frame_index()
        elif (self._cache.width, self._cache.height) != (width, height):
            self._cache = frame.scaled(width, height)
        image = self._cache
        x = self.rect.x + (self.rect.w - image.width) / 2
        y = self.rect.y + (self.rect.h - image.height) / 2
        canvas.blit(image, int(x), int(y))

    def close(self):
        if self.stream is not None:
            self.stream.close()
            self.stream = None

    def mouse_up(self, x, y, button="left"):
        if self.playing:
            self.pause()
        else:
            self.play()

    def key_down(self, key, modifiers=0):
        if key == 32:  # space
            self.mouse_up(0, 0)


class DockPane:
    def __init__(self, title, widget, area="left", size=220):
        self.tabs = [(title, widget)]
        self.active = 0
        self.area = area
        self.size = int(size)
        self.widget.parent = None

    @property
    def title(self):
        return self.tabs[self.active][0]

    @property
    def widget(self):
        return self.tabs[self.active][1]

    def add_tab(self, title, widget):
        self.tabs.append((title, widget))
        self.active = len(self.tabs) - 1
        return self

    def select(self, index):
        self.active = max(0, min(len(self.tabs) - 1, index))
        return self.widget


class DockManager(Widget):
    def __init__(self, central=None):
        super().__init__()
        self.central = central or Panel()
        self.central.parent = self
        self.panes = []
        self.layouts = {}
        self._drag = None

    def add_pane(self, title, widget, area="left", size=220):
        pane = DockPane(title, widget, area, size)
        self.panes.append(pane)
        widget.parent = self
        return pane

    def state(self):
        return [{"area": pane.area, "size": pane.size,
                 "active": pane.active,
                 "tabs": [title for title, _widget in pane.tabs]}
                for pane in self.panes]

    def save_layout(self, name):
        self.layouts[str(name)] = self.state()
        return self

    def apply_layout(self, name):
        state = self.layouts.get(str(name))
        if state is None:
            return False
        for pane, saved in zip(self.panes, state):
            pane.area = saved.get("area", pane.area)
            pane.size = int(saved.get("size", pane.size))
            pane.active = max(0, min(len(pane.tabs) - 1,
                                     int(saved.get("active", 0))))
        self.arrange(self.rect)
        return True

    def save_presets(self, settings, key="dock_presets"):
        settings.set(key, self.layouts)
        return self

    def load_presets(self, settings, key="dock_presets"):
        self.layouts = dict(settings.get(key, {}))
        return self

    def save_state(self, settings, key="docking"):
        settings.set(key, self.state())
        return self

    def load_state(self, settings, key="docking"):
        for pane, saved in zip(self.panes, settings.get(key, [])):
            pane.area = saved.get("area", pane.area)
            pane.size = int(saved.get("size", pane.size))
            pane.active = max(0, min(len(pane.tabs) - 1,
                                     int(saved.get("active", 0))))
        self.arrange(self.rect)
        return self

    def size_hint(self):
        return (720, 480)

    def arrange(self, rect):
        self.rect = rect
        left = [p for p in self.panes if p.area == "left"]
        right = [p for p in self.panes if p.area == "right"]
        bottom = [p for p in self.panes if p.area == "bottom"]
        x = rect.x
        y = rect.y
        width = rect.w
        height = rect.h
        left_width = sum(p.size for p in left)
        right_width = sum(p.size for p in right)
        bottom_height = sum(p.size for p in bottom)
        for index, pane in enumerate(left):
            pane.widget.arrange(Rect(x, y + 24, pane.size,
                                     max(1, height - bottom_height - 24)))
            x += pane.size
            width -= pane.size
        for index, pane in enumerate(right):
            pane.widget.arrange(Rect(rect.right - (index + 1) * pane.size,
                                     y + 24, pane.size,
                                     max(1, height - bottom_height - 24)))
            width -= pane.size
        for index, pane in enumerate(bottom):
            pane.widget.arrange(Rect(x, rect.bottom - (index + 1) * pane.size,
                                     width, max(1, pane.size - 24)))
            height -= pane.size
        self.central.arrange(Rect(x, y, max(1, width), max(1, height)))

    def _dividers(self):
        dividers = []
        left = [p for p in self.panes if p.area == "left"]
        right = [p for p in self.panes if p.area == "right"]
        bottom = [p for p in self.panes if p.area == "bottom"]
        x = self.rect.x
        for pane in left:
            x += pane.size
            dividers.append(("left", pane, x))
        x = self.rect.right
        for pane in right:
            x -= pane.size
            dividers.append(("right", pane, x))
        y = self.rect.bottom
        for pane in bottom:
            y -= pane.size
            dividers.append(("bottom", pane, y))
        return dividers

    def mouse_down(self, x, y, button="left"):
        for area, pane, position in self._dividers():
            if area in ("left", "right") and abs(x - position) <= 4:
                self._drag = (area, pane, x)
                return
            if area == "bottom" and abs(y - position) <= 4:
                self._drag = (area, pane, y)
                return

    def mouse_move(self, x, y):
        if self._drag is None:
            return
        area, pane, origin = self._drag
        if area == "left":
            pane.size = max(80, pane.size + (x - origin))
        elif area == "right":
            pane.size = max(80, pane.size - (x - origin))
        else:
            pane.size = max(50, pane.size - (y - origin))
        self._drag = (area, pane, x if area != "bottom" else y)
        self.arrange(self.rect)

    def mouse_up(self, x, y, button="left"):
        for pane in self.panes:
            rect = pane.widget.rect
            if rect.y - 24 <= y < rect.y:
                tab_width = max(80, rect.w // max(1, len(pane.tabs)))
                index = int((x - rect.x) // tab_width)
                if 0 <= index < len(pane.tabs):
                    pane.select(index)
                    self.arrange(self.rect)
                    self._drag = None
                    return
        self._drag = None

    def float_pane(self, pane):
        from .window import Window
        if pane not in self.panes:
            return None
        self.panes.remove(pane)
        window = Window(pane.title, 480, 320)
        window.root.children.clear()
        window.root.add(pane.widget)
        pane.widget.parent = window.root
        window._layout_root()
        window.docked_pane = pane
        window.on_close = lambda: self.redock(window)
        self.arrange(self.rect)
        return window

    def redock(self, window):
        pane = getattr(window, "docked_pane", None)
        if pane is None:
            return None
        if pane not in self.panes:
            self.panes.append(pane)
        pane.widget.parent = self
        window.root.children.clear()
        self.arrange(self.rect)
        return pane

    def paint(self, canvas):
        theme = self.theme()
        self.central.paint(canvas)
        for pane in self.panes:
            rect = pane.widget.rect
            canvas.fill_rect(rect, theme.surface_alt)
            tab_width = max(80, rect.w // max(1, len(pane.tabs)))
            for index, (title, _widget) in enumerate(pane.tabs):
                tab = Rect(rect.x + index * tab_width, rect.y - 24,
                           tab_width, 24)
                if index == pane.active:
                    canvas.fill_rect(tab, theme.accent.with_alpha(80))
                draw_text(canvas, title, tab.x + 6, tab.y + 6, theme.text, 2)
            pane.widget.paint(canvas)
