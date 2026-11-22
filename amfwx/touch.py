"""AMFWX touch events and multi-touch gesture recognition."""

from __future__ import annotations

import math
import time
from dataclasses import dataclass


@dataclass
class TouchEvent:
    id: int = 0
    x: int = 0
    y: int = 0
    state: str = "move"
    primary: bool = False
    pressure: float = 0.0


@dataclass
class GestureEvent:
    kind: str = "tap"
    x: int = 0
    y: int = 0
    dx: float = 0.0
    dy: float = 0.0
    scale: float = 1.0
    rotation: float = 0.0
    direction: str = ""
    points: int = 1


class GestureRecognizer:
    def __init__(self, tap_slop=12, tap_timeout=0.35):
        self.tap_slop = tap_slop
        self.tap_timeout = tap_timeout
        self.listeners = []
        self._points = {}
        self._start = 0.0
        self._start_center = (0.0, 0.0)
        self._last_center = (0.0, 0.0)
        self._last_distance = 0.0
        self._last_angle = 0.0
        self._moved = False

    def connect(self, callback):
        self.listeners.append(callback)
        return callback

    def _emit(self, event):
        for callback in list(self.listeners):
            callback(event)

    def _center(self):
        if not self._points:
            return (0.0, 0.0)
        xs = [point[0] for point in self._points.values()]
        ys = [point[1] for point in self._points.values()]
        return (sum(xs) / len(xs), sum(ys) / len(ys))

    def _distance(self):
        points = list(self._points.values())
        return math.dist(points[0], points[1]) if len(points) >= 2 else 0.0

    def _angle(self):
        points = list(self._points.values())
        if len(points) < 2:
            return 0.0
        return math.atan2(points[1][1] - points[0][1],
                          points[1][0] - points[0][0])

    def touch(self, point_id, x, y, state):
        x, y = float(x), float(y)
        if state == "down":
            if not self._points:
                self._start = time.monotonic()
                self._start_center = (x, y)
            self._points[point_id] = (x, y)
            if len(self._points) >= 2:
                self._last_distance = self._distance()
                self._last_angle = self._angle()
            self._last_center = self._center()
            return
        if point_id not in self._points:
            return
        if state == "move":
            self._points[point_id] = (x, y)
            center = self._center()
            dx = center[0] - self._last_center[0]
            dy = center[1] - self._last_center[1]
            if abs(dx) + abs(dy) > 1.5:
                self._moved = True
            if len(self._points) >= 2:
                distance = self._distance()
                angle = self._angle()
                scale = distance / self._last_distance if self._last_distance else 1.0
                rotation = angle - self._last_angle
                self._last_distance = distance
                self._last_angle = angle
                self._emit(GestureEvent("pinch", int(center[0]),
                                        int(center[1]), scale=scale,
                                        points=len(self._points)))
                if abs(rotation) > 0.01:
                    self._emit(GestureEvent("rotate", int(center[0]),
                                            int(center[1]),
                                            rotation=rotation,
                                            points=len(self._points)))
            self._emit(GestureEvent("pan", int(center[0]), int(center[1]),
                                    dx=dx, dy=dy, points=len(self._points)))
            self._last_center = center
            return
        if state == "up":
            center = self._center()
            dx = center[0] - self._start_center[0]
            dy = center[1] - self._start_center[1]
            elapsed = time.monotonic() - self._start
            if len(self._points) == 1 and not self._moved and elapsed <= self.tap_timeout:
                self._emit(GestureEvent("tap", int(center[0]), int(center[1])))
            elif len(self._points) == 1 and abs(dx) + abs(dy) > self.tap_slop:
                direction = ("right" if abs(dx) > abs(dy) and dx > 0 else
                             "left" if abs(dx) > abs(dy) else
                             "down" if dy > 0 else "up")
                self._emit(GestureEvent("swipe", int(center[0]),
                                        int(center[1]), dx=dx, dy=dy,
                                        direction=direction))
            self._points.pop(point_id, None)
            if not self._points:
                self._moved = False
            elif len(self._points) == 1:
                self._last_center = self._center()
